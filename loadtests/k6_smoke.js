import http from 'k6/http';
import { check } from 'k6';

export const options = {
  vus: Number(__ENV.VUS || 20),
  duration: __ENV.DURATION || '30s',
  thresholds: {
    http_req_failed: ['rate<0.001'],
    http_req_duration: ['p(95)<250'],
  },
};

export default function () {
  const base = __ENV.BASE_URL || 'http://127.0.0.1:8000';
  const token = __ENV.TOKEN || '';
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const res = http.get(`${base}/enterprise/health`, { headers });
  check(res, { 'health 200': (r) => r.status === 200 });
}
