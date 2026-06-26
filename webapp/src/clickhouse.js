export async function queryClickHouse(queryStr) {
  const url = 'https://eguolg5o2j.eu-west-2.aws.clickhouse.cloud:8443/';
  const auth = btoa('default:98tJ0X.uCexVL');
  
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${auth}`,
    },
    body: `${queryStr} FORMAT JSON`
  });
  
  if (!res.ok) {
    throw new Error(`ClickHouse query failed: ${await res.text()}`);
  }
  
  return res.json();
}
