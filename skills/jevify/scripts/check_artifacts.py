#!/usr/bin/env python3
"""Check audit/parity artifact shape, not model truth or transcript compliance.

This read-only check never fills missing measurements, edits records, selects a
threshold, or certifies that a provider was actually called.
"""
import argparse,hashlib,json,math,pathlib,re

def finite(v):return type(v) in (int,float) and math.isfinite(v)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('output',type=pathlib.Path)
    p.add_argument('--require-live',action='store_true')
    a=p.parse_args();errors=[]
    def require(ok,why):
        if not ok:errors.append(why)
    def read(name):
        try:return json.loads((a.output/name).read_text())
        except (OSError,ValueError) as e:
            errors.append(name+': '+type(e).__name__);return {}
    for f in ['JEV_CONVERSION_PLAN.md','JEV_CONVERSION_REPORT.md']:
        require((a.output/f).is_file(),'missing '+f)
    audit=read('JEV_AUDIT.json')
    sites=audit.get('sites',[])
    require(isinstance(sites,list),'sites must be an array')
    for site in sites:
        sid=str(site.get('file'))+':'+str(site.get('line'))
        require(type(site.get('line')) is int and site['line']>0,sid+': positive line required')
        for field in ['file','provider','downstream','fit','reason']:
            require(bool(site.get(field)),sid+': missing '+field)
        require(site.get('classification') in ['DECISION','GENERATION','MIXED','EXTRACTION'],sid+': invalid classification')
        opts=site.get('options',[]);require(1<=len(opts)<=3,sid+': need 1–3 options')
        for opt in opts:
            for field in ['action','primitive','benefit','risk']:
                require(isinstance(opt.get(field),str) and bool(opt[field]),sid+': '+field+' must be a nonempty string (use "none" for no primitive)')
            require(not(site.get('classification')=='GENERATION' and opt.get('action')=='jev_only'),sid+': generation cannot be Jev-only')
    converted=audit.get('converted_sites')
    require(isinstance(converted,list),'converted_sites must be an array of original file:line IDs')
    if converted and a.require_live:
        evidence=read('JEV_PARITY.json');by={s.get('site_id'):s for s in evidence.get('sites',[])}
        for sid in converted:
            item=by.get(sid,{})
            rows=item.get('rows',[])
            require(len({hashlib.sha256(json.dumps(r.get('input'),sort_keys=True).encode()).hexdigest() for r in rows})>=30,sid+': need 30 unique live pairs')
            noul=item.get('primitive')=='Noul'
            if noul:
                band=item.get('abstention_band',[])
                require(isinstance(band,list) and len(band)==2 and all(finite(v) for v in band) and 0<=band[0]<band[1]<=1,sid+': invalid Noul abstention band')
            else:
                threshold=item.get('threshold');require(finite(threshold) and 0<=threshold<=1,sid+': invalid threshold')
            for i,r in enumerate(rows):
                loc=f'{sid} row {i}'
                require(r.get('provenance') in ['repo','synthetic'],loc+': provenance must be repo or synthetic; put path in source')
                require(r.get('live') is True and bool(r.get('request_id')),loc+': actual live request ID required')
                require(bool(re.search(r'(?:^|/)jev-\d+\.\d+(?:\.\d+|-\d{8})$',str(r.get('model','')))),loc+': versioned Jev model required')
                require(bool(r.get('original_model')),loc+': original model required')
                for f in ['jev_answer','original_answer']:require(r.get(f) is not None,loc+': missing '+f)
                for f in ['latency_ms','cost_usd','original_latency_ms','original_cost_usd']:
                    require(finite(r.get(f)) and r[f]>=0,loc+': missing actual metric/explicit estimate '+f)
                require(type(r.get('fallback_taken')) is bool,loc+': fallback boolean required')
                if noul:
                    require('confidence' not in r,loc+': Noul has no confidence')
                    v=r.get('probability');require(finite(v) and 0<=v<=1,loc+': invalid probability')
                else:
                    v=r.get('confidence');require(finite(v) and 0<=v<=1,loc+': invalid confidence')
                    if finite(v) and finite(item.get('threshold')):
                        require(r.get('fallback_taken')==(v<item['threshold'] or bool(r.get('error'))),loc+': fallback disagrees with chosen gate')
            for fault in ['below_threshold','error','timeout','rate_limit']:
                require(item.get('faults',{}).get(fault) is True,sid+': executed '+fault+' assertion required')
    print(json.dumps({'shape_valid':not errors,'errors':errors,'notice':'Shape only; manually verify live provenance, contracts, confidence agreement and approval evidence.'},indent=2))
    return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
