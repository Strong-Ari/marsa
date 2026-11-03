"""LLM backends. Everything downstream treats the model as untrusted: output is parsed, gated and logged."""
import hashlib, json, os, re, urllib.request
SCHEMA={"type":"object","properties":{"reasoning":{"type":"string","maxLength":240},"position":{"type":"string","enum":["support","oppose","conditional","no_position"]},
 "recommendation":{"type":"string","maxLength":260},"claims":{"type":"array","maxItems":3,"items":{"type":"object","properties":{"claim":{"type":"string","maxLength":170},"sentence":{"type":"integer"}},"required":["claim","sentence"]}}},
 "required":["reasoning","position","recommendation","claims"]}
def repair(t):
    """Local models can stop mid-JSON at the token limit. Keep complete claims and drop the rest."""
    try: return json.loads(t)
    except json.JSONDecodeError: pass
    for end in ("]}","\"}]}"):
        i=t.rfind("},")
        if i>0:
            try: return json.loads(t[:i+1]+"]"+"}")
            except json.JSONDecodeError: pass
    g=lambda k:(re.search(rf'"{k}"\s*:\s*"((?:[^"\\\\]|\\\\.)*)"',t) or [None,""])[1]
    return {"reasoning":g("reasoning"),"position":g("position") or "no_position","recommendation":g("recommendation") or "Escalate to a human.","claims":[]}
class Extractive:
    """No model: quotes the best sentence from each source. Keeps the demo runnable anywhere."""
    name="extractive-v1"
    def assess(self,system,user,sources,query):
        S=sources[0]["sentences"]; terms=set(re.findall(r"[a-z]{4,}",query.lower())); seen=set(); claims=[]
        for i in sorted(range(len(S)),key=lambda i:-len(terms&set(re.findall(r"[a-z]{4,}",S[i][1].lower())))):
            if S[i][0]["cid"] in seen: continue
            seen.add(S[i][0]["cid"]); claims.append({"claim":f"Relevant text in {S[i][0]['title'][:80]}.","sentence":i+1})
            if len(claims)==3: break
        return {"reasoning":"Extractive mode: selected the sentences that best overlap the event and action.","position":"conditional","recommendation":"Apply the cited text and refer undecided points to the named authority.","claims":claims}
class LlamaCpp:
    def __init__(self,path,n_ctx=4096,threads=2):
        from llama_cpp import Llama
        self.m=Llama(model_path=path,n_ctx=n_ctx,n_threads=threads,verbose=False); self.name=os.path.basename(path)
    def assess(self,system,user,sources,query):
        r=self.m.create_chat_completion(messages=[{"role":"system","content":system},{"role":"user","content":user}],temperature=0.1,max_tokens=300,seed=7,
            response_format={"type":"json_object","schema":SCHEMA})
        t=r["choices"][0]["message"]["content"]
        return repair(t)
class OpenAICompat:
    """Any OpenAI-compatible endpoint, including Ollama (http://localhost:11434/v1)."""
    def __init__(self,base,model,key=None):
        self.base,self.model,self.key=base.rstrip("/"),model,key or os.environ.get("MARSA_API_KEY","none"); self.name=model
    def assess(self,system,user,sources,query):
        b=json.dumps({"model":self.model,"temperature":0.1,"seed":7,"response_format":{"type":"json_object"},
            "messages":[{"role":"system","content":system+"\nReturn JSON only with keys reasoning, position (support, oppose, conditional or no_position), recommendation, claims (list of objects with claim and sentence)."},{"role":"user","content":user}]}).encode()
        q=urllib.request.Request(self.base+"/chat/completions",b,{"Content-Type":"application/json","Authorization":"Bearer "+self.key})
        t=json.load(urllib.request.urlopen(q,timeout=300))["choices"][0]["message"]["content"]
        return json.loads(t[t.find("{"):t.rfind("}")+1])
def make(spec):
    if spec=="extractive": return Extractive()
    if spec.startswith("gguf:"): return LlamaCpp(spec[5:])
    if spec.startswith("openai:"):
        base,model=spec[7:].rsplit("|",1); return OpenAICompat(base,model)
    raise ValueError(spec)
def digest(*p): return hashlib.sha256("\n".join(p).encode()).hexdigest()[:16]
