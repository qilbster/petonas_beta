from databricks_api import DatabricksAPI
import time

def call_api(job_id, input_params):
    db = DatabricksAPI(
    host = "https://dbc-eb788f31-6c73.cloud.databricks.com/",
    token = "dapi52ff828b8575edb2585ede0beff0dcbb"
    )
    run_id = db.jobs.run_now(job_id=job_id, notebook_params=input_params).get('run_id')
    run_status = db.jobs.get_run(run_id)['state']['life_cycle_state']
    start_time = time.time()
    while (time.time()-start_time < 300 and run_status != 'TERMINATED'):
        time.sleep(10)
        run_status = db.jobs.get_run(run_id)['state']['life_cycle_state']

    if db.jobs.get_run(run_id)['state'].get('result_state') == 'SUCCESS':
        return db.jobs.get_run_output(run_id)['notebook_output']['result']





