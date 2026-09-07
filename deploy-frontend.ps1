cd "C:\dev\flowbill\frontend"
npm run build
ssh -i "C:\secure\Documents_AWS\portfolio-api-key-2.pem" ubuntu@52.3.232.204 "rm -rf /var/www/flowbill/dist"
scp -i "C:\secure\Documents_AWS\portfolio-api-key-2.pem" -r "C:\dev\flowbill\frontend\dist\." ubuntu@52.3.232.204:/var/www/flowbill/dist/
