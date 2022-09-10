var https = require('https');
const options = {
  host: process.env.VPCE_DNS_NAME,
  port: 443,
  path: '/demo/pets',
  method: 'GET',
  headers: {
    'Host':process.env.API_GW_ENDPOINT
  }
};
exports.handler = (event, context, callback) => {
    https.request(options, (res) => {
      console.log('statusCode:', res.statusCode);
      console.log('headers:', res.headers);
      let data = '';
      res.on('data', (d) => {
       data += d;
        process.stdout.write(d);
      });
      res.on('end', () => {
         callback(null, JSON.parse(data));
      });
    }).on('error', (e) => {
      console.error(e);
      callback(null, e);
    }).end();
};