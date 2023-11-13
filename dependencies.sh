# pip download PyNaCl --platform manylinux1_x86_64 --no-deps -d venv/lib/python3.10/site-packages
# pip download cffi --platform manylinux1_x86_64 --no-deps -d venv/lib/python3.10/site-packages
# pip download bcrypt --platform manylinux1_x86_64 --no-deps -d venv/lib/python3.10/site-packages
# pip download cryptography --platform manylinux2014_x86_64 --no-deps -d venv/lib/python3.10/site-packages

cd venv/lib/python3.10/site-packages
unzip \*.whl
# for file in *.tar.gz
# do
#     tar -xzf "$file"
# done
# rm *.whl
cd ../../../../