cd /Users/massaud/Documents/Codes/FisherApp/venv/lib/python3.10/site-packages

# Delete function.zip if it exists
if [ -f ../../../../function.zip ]; then
  rm ../../../../function.zip
fi

# Create a new function.zip excluding the pip folder and other unnecessary packages
zip -r9 ../../../../function.zip . \
    -x '*uvicorn*' \
    -x '*pip*' \
    -x '*astroid*' \
    -x '*isort*' \
    -x '*mypy*' \
    -x '*pylint*' \
    -x '*pyproject_hooks*' \
    -x '*build*' \
    -x '*installer*' \
    -x '*pkginfo*' \
    -x '*virtualenv*' \
    -x '*alembic*' \
    -x '*Mako*'

cd ../../../../
zip -g ./function.zip -r app \
    -x '*uvicorn*' \
    -x '*pip*' \
    -x '*astroid*' \
    -x '*isort*' \
    -x '*mypy*' \
    -x '*pylint*' \
    -x '*pyproject_hooks*' \
    -x '*build*' \
    -x '*installer*' \
    -x '*pkginfo*' \
    -x '*virtualenv*' \
    -x '*alembic*' \
    -x '*Mako*'
