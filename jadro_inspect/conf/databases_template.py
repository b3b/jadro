# Auto generated

DATABASES = {
    {% for name, db in databases.items %}'{{name}}': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': '{{db.NAME}}'},
    {% endfor %}
    }
