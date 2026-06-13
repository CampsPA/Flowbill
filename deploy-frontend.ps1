cd "C:\Users\campo\OneDrive\Desktop\flowbill\frontend"
npm run build
ssh -i "C:\Users\campo\OneDrive\Desktop\AWS_Deployment\Documents_AWS\portfolio-api-key-2.pem" ubuntu@52.3.232.204 "rm -rf /var/www/flowbill/dist"
scp -i "C:\Users\campo\OneDrive\Desktop\AWS_Deployment\Documents_AWS\portfolio-api-key-2.pem" -r "C:\Users\campo\OneDrive\Desktop\flowbill\frontend\dist\." ubuntu@52.3.232.204:/var/www/flowbill/dist/
