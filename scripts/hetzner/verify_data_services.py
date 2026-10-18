"""Read-only authenticated probes; run on the deployment host. Never print secrets."""
import base64
import datetime
import hashlib
import hmac
import json
import pathlib
import urllib.request
import uuid


def main():
    env = {}
    for line in pathlib.Path('/opt/clisonix.com/.env').read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            env[key] = value.strip().strip('\"\'')
    records = []
    for service in ['neo4j', 'minio']:
        record = {'service': service, 'execution_id': str(uuid.uuid4()),
                  'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()}
        try:
            if service == 'neo4j':
                auth = base64.b64encode(('neo4j:' + env['NEO4J_PASSWORD']).encode()).decode()
                request = urllib.request.Request(
                    'http://127.0.0.1:7474/db/neo4j/tx/commit',
                    data=json.dumps({'statements': [{'statement': 'RETURN 17 * 23 AS result'}]}).encode(),
                    headers={'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'})
            else:
                host = '127.0.0.1:9000'
                now = datetime.datetime.now(datetime.timezone.utc)
                stamp, date = now.strftime('%Y%m%dT%H%M%SZ'), now.strftime('%Y%m%d')
                digest = hashlib.sha256(b'').hexdigest()
                headers = f'host:{host}\nx-amz-content-sha256:{digest}\nx-amz-date:{stamp}\n'
                signed = 'host;x-amz-content-sha256;x-amz-date'
                canonical = 'GET\n/\n\n' + headers + '\n' + signed + '\n' + digest
                scope = date + '/us-east-1/s3/aws4_request'
                to_sign = 'AWS4-HMAC-SHA256\n' + stamp + '\n' + scope + '\n' + hashlib.sha256(canonical.encode()).hexdigest()
                key = ('AWS4' + env['MINIO_ROOT_PASSWORD']).encode()
                for item in [date, 'us-east-1', 's3', 'aws4_request']:
                    key = hmac.new(key, item.encode(), hashlib.sha256).digest()
                signature = hmac.new(key, to_sign.encode(), hashlib.sha256).hexdigest()
                auth = 'AWS4-HMAC-SHA256 Credential=' + env['MINIO_ROOT_USER'] + '/' + scope + ', SignedHeaders=' + signed + ', Signature=' + signature
                request = urllib.request.Request('http://' + host + '/', headers={
                    'Authorization': auth, 'x-amz-date': stamp, 'x-amz-content-sha256': digest})
            with urllib.request.urlopen(request, timeout=15) as response:
                output = response.read()
                record.update(http=response.status, output_sha256=hashlib.sha256(output).hexdigest())
                if service == 'neo4j':
                    data = json.loads(output)
                    record['passed'] = not data.get('errors') and data['results'][0]['data'][0]['row'] == [391]
                else:
                    record['passed'] = b'ListAllMyBucketsResult' in output
        except Exception as exc:
            record.update(passed=False, error=type(exc).__name__)
        records.append(record)
    print(json.dumps({'scope': 'authenticated read-only data-service execution', 'executions': records}))
    return 0 if all(row['passed'] for row in records) else 1


if __name__ == '__main__':
    raise SystemExit(main())
