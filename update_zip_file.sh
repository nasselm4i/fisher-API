cd /Users/massaud/Documents/Codes/FisherApp/venv/lib/python3.10/site-packages

# Delete function.zip if it exists
if [ -f ../../../../function.zip ]; then
  rm ../../../../function.zip
fi

# Create a new function.zip
zip -r9 ../../../../function.zip .

cd ../../../../
zip -g ./function.zip -r app