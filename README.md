# qmra
Web-application for calculating microbial risk for drinking water and water reuse systems.

## Installation

create a venv
```bash
python -m venv venv
```

source it (Mac/Linux)
```bash
source venv/bin/activate
```
or on windows
```bash
source venv/Scripts/activate
```

then, install the requirements with 
```bash
pip install -r requirements.txt
```

collect the statics and migrate with
```bash
python manage.py collectstatic
python manage.py migrate
```

run the app locally

```bash
python manage.py runserver
```


