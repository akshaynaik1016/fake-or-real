"""Run offline with an isolated temporary DB; never touches included databases."""
import os,tempfile,asyncio,json,argparse
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='fake-or-real-evaluation-') as directory:
        os.environ.update(DATABASE_URL='sqlite:///'+str(Path(directory)/'evaluation.db'),ENVIRONMENT='development',DEMO_MODE='true',AI_PROVIDER='none',
            TAVILY_API_KEY='',SAFE_BROWSING_API_KEY='',VIRUSTOTAL_API_KEY='',NETWORK_SCANNERS_ENABLED='false',CASE_URL_FETCH_ENABLED='false')
        from app.main import app
        from app.core.database import SessionLocal
        from app.evaluation.runner import dataset,run_scenario,metrics
        async def evaluate():
            results=[]
            with SessionLocal() as db:
                for scenario in dataset()['scenarios']:
                    result=await run_scenario(db,scenario)
                    results.append({k:v for k,v in result.items() if k!='case'})
            payload={'dataset':{k:v for k,v in dataset().items() if k!='scenarios'},'metrics':metrics(results),'results':results}
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(payload,indent=2,ensure_ascii=False))
            print(json.dumps(payload['metrics'],indent=2))
            for result in results:
                if not result['passed']:print('FAILED',result['scenario_id'],json.dumps([c for c in result['checks'] if not c['passed']],ensure_ascii=False))
            return 0 if all(r['passed'] for r in results) else 1
        return asyncio.run(evaluate())
if __name__=='__main__':raise SystemExit(main())
