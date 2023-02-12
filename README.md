# pyFinance

todo: add example data

## installation
if using virtual environment...
```bash
# set venv path and name to whereever you like
python -m venv ~/path/to/pyfinance-env

cd /path/to/pyFinance
source ~/path/to/pyfinance-env/bin/activate
```

install required packages...
```bash
# install required packages
pip install -r requirements.txt
```

## Docker
```bash
docker build -t pyfinance .
# go to the data directory and run your program, e.g.
docker run --rm -it -v ${pwd}:/workdir pyfinance python main.py
```

## track expense
download CSV and label expenses once in a while

* [CSX](https://direct.credit-suisse.com/dn/c/cls/auth?language=en)
* Wise

for others, add by hand...

## track net worth
input data from different sources manually?
