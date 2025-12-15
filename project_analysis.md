# Анализ проекта

**Папка**: `ompbot`

## 📁 Структура

```
.env (265B)
.github/workflows/deploy.yml (2.2KB)
.gitignore (62B)
Dockerfile (623B)
README.md (657B)
data/metrics.yaml (6.8KB)
data/py.log (35.9KB)
data/received_docs.json (20.8KB)
data/reconciliation_report.json (100B)
data/sent_docs.json (2B)
entrypoint.sh (472B)
ignored.txt (0B)
main.py (2.6KB)
ompbot.py (25.8KB)
project_analysis.md (0B)
project_to_text.py (3.4KB)
requirements.txt (60B)
setup.py (904B)
test_mail_helper.py (1.1KB)
test_mail_helper_simple.py (1.1KB)
users.yml (0B)
utils/__init__.py (439B)
utils/__init__.pyc (570B)
utils/excel_helper.py (6.3KB)
utils/ignored_list.py (1.6KB)
utils/log.py (664B)
utils/mail_helper.py (4.2KB)
utils/mail_integration_helpers.py (2.0KB)
utils/mail_poller.py (1.5KB)
utils/mail_reciever.py (10.7KB)
utils/mail_sync_worker.py (3.8KB)
utils/metrics.py (4.1KB)
utils/net_helper.py (535B)
utils/user_list.py (2.8KB)
utils/vk_helper.py (6.2KB)
```

## 📄 Исходный код

### `.github/workflows/deploy.yml`

```yaml
name: Deploy on Push

on:
  push:
    branches: [ master, dev ]
  pull_request:
    branches: [ master, dev ]

permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
  
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8
          pip install -r requirements.txt
  
      - name: Run linter - hard errors only
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Run linter - soft style guide
        run: |
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
  build-and-push:
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR (via PAT)
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: 'enderdissa'
          password: ${{ secrets.GHCR_PUSH_TOKEN }}
      - name: Build & Tag
        run: |
          OWNER=$(echo "${{ github.repository_owner }}" | tr '[:upper:]' '[:lower:]')
          IMAGE="ghcr.io/${OWNER}/ompbot"
          docker build -t $IMAGE:latest -f ./Dockerfile .
          docker tag $IMAGE:latest $IMAGE:${{ github.run_number }}
          echo "IMAGE=$IMAGE" >> $GITHUB_ENV
      - name: Push
        run: |
          docker push $IMAGE:latest
          docker push $IMAGE:${{ github.run_number }}
  # deploy:
  #     needs: test
  #     runs-on: ubuntu-latest
  #     steps:
  #       - name: Execute SSH Commands
  #         uses: GPTED/SSH-My-Action@0.1
  #         with:
  #           HOST: 45.93.200.157
  #           USER: bot_dev
  #           PORT: 22
  #           PRIVATE_KEY: ${{ secrets.BOT_DEV_SSH_PRIVATE_KEY }}
  #           CMD: |
  #             cd /srv/bots/vk-ompbot/app/ompbot;
  #             git reset --hard HEAD;
  #             git pull;
  #             cd /srv/bots/vk-ompbot;
  #             docker compose up -d --build --force-recreate;

```

### `.gitignore`

```text
.idea/*
token.txt
ignored.txt
*.xlsx
*.docx
*.log
*.yml
*.yaml
```

### `Dockerfile`

```text
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash bot \
  && mkdir -p /app && chown bot:bot /app

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN chown -R bot:bot /app
RUN chmod +x /app/entrypoint.sh

USER bot
WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]

```

### `README.md`

```markdown
# ompbot
![Static Badge](https://img.shields.io/badge/EnderDissa-ompbot-ompbot)
![GitHub top language](https://img.shields.io/github/languages/top/EnderDissa/ompbot)


HOWTO:
1) git clone
2) pip install -r ./requirements.py (installing requirements)
3) python setup.py (created neccesarry dirs and files, asking for token)
4) python main.py (running bot itself)

Рекомендую добавить ompbot.py в параметры автозапуска и настроить параметры энергосбережения (на рабочем ПК) или запустить создать ../compose.yml (на нормальном сервере)


```

### `data/metrics.yaml`

```yaml
errors: 61
history:
- event: error
  timestamp: '2025-12-15T02:56:22.730169'
  trigger: 'HTTPSConnectionPool(host=''lp.vk.com'', port=443): Read timed out. (read
    timeout=35)'
- event: error
  timestamp: '2025-12-15T02:56:22.941553'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.044912'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.181175'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.284652'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.390311'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.501468'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.612478'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.724475'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.859483'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.992722'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.101742'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.248581'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.411370'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.549754'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.710115'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.872071'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.010813'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.163192'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.336478'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.529007'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.653380'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.789061'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.034605'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.238364'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.382184'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.539105'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.678190'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.816852'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.980272'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.109196'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.239990'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.375283'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.544715'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.706780'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.885789'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.028567'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.165504'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.335332'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.482787'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.620418'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.788303'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.917986'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.068099'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.214737'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.383542'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.534822'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.696020'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.847950'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.000148'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.159784'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.313671'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.474937'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.616078'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.762823'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.909967'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.078591'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.274205'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.444006'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.587128'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.768939'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
manager: 0
memo_approved: 0
memo_filtered: 0
memo_received: 0
message: 0

```

### `data/received_docs.json`

```json
{
  "7f4669b6526b45cb": {
    "id": "7f4669b6526b45cb",
    "email_id": "280",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Mon, 08 Dec 2025 12:42:47 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.067365"
  },
  "331d12d44d3f8160": {
    "id": "331d12d44d3f8160",
    "email_id": "281",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Mon, 08 Dec 2025 13:00:24 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.132572"
  },
  "99694232a4e14995": {
    "id": "99694232a4e14995",
    "email_id": "282",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Mon, 08 Dec 2025 16:32:30 +0300",
    "body": "\nДобрый день!\n \nСлужебная записка согласована и внесена в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.204338"
  },
  "39b35e944f9fce2b": {
    "id": "39b35e944f9fce2b",
    "email_id": "283",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Tue, 09 Dec 2025 14:19:20 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n   \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < omp",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.323230"
  },
  "240da7d088b388bc": {
    "id": "240da7d088b388bc",
    "email_id": "284",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Wed, 10 Dec 2025 10:49:53 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.387651"
  },
  "d01d32f599b56114": {
    "id": "d01d32f599b56114",
    "email_id": "285",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Wed, 10 Dec 2025 12:47:04 +0300",
    "body": "\nДобрый день!\n \nСлужебная записка согласована и внесена в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.460611"
  },
  "7ba843e1b8a4b993": {
    "id": "7ba843e1b8a4b993",
    "email_id": "286",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Wed, 10 Dec 2025 13:51:57 +0300",
    "body": "\nДобрый день!\n \nСлужебная записка согласована и внесена в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.538636"
  },
  "d095a8dedb28337b": {
    "id": "d095a8dedb28337b",
    "email_id": "287",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Thu, 11 Dec 2025 12:32:22 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.612264"
  },
  "1efc6cbd24800010": {
    "id": "1efc6cbd24800010",
    "email_id": "288",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Thu, 11 Dec 2025 16:39:53 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны. Прикладываем согласованную СЗ для передачи на пост охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 19710",
    "attachments": [
      {
        "filename": "=?UTF-8?B?MDM1LnBkZg==?=",
        "content_type": "application/pdf",
        "size": 400496
      }
    ],
    "received_at": "2025-12-15T02:56:03.949540"
  },
  "50f07f098f4a18f8": {
    "id": "50f07f098f4a18f8",
    "email_id": "289",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Fri, 12 Dec 2025 13:51:10 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:04.488589"
  },
  "309b828201746d27": {
    "id": "309b828201746d27",
    "email_id": "290",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Fri, 12 Dec 2025 15:14:17 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < omp@i",
    "attachments": [],
    "received_at": "2025-12-15T02:56:04.572295"
  },
  "3b04cfd1fe60c063": {
    "id": "3b04cfd1fe60c063",
    "email_id": "291",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Fri, 12 Dec 2025 16:50:57 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [
      {
        "filename": "=?UTF-8?B?U1pfVGVhdHJaYXZ0cmFfMjAyNS0xMi0xMl8xNS00Ni0yNC5wZGY=?=",
        "content_type": "application/pdf",
        "size": 402234
      },
      {
        "filename": "=?UTF-8?B?U1pfVGVhdHJaYXZ0cmFfMjAyNS0xMi0xMl8xNS00NS01MSAoMSkucGRm?=",
        "content_type": "application/pdf",
        "size": 402233
      }
    ],
    "received_at": "2025-12-15T02:56:04.974460"
  },
  "29d4218c45166a8e": {
    "id": "29d4218c45166a8e",
    "email_id": "292",
    "subject": "Согласование СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:54:59.344093",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:54:59.344175"
  },
  "0f2cc4342bafd9f6": {
    "id": "0f2cc4342bafd9f6",
    "email_id": "293",
    "subject": "Re: Согласование СЗ",
    "sender": "Берман Денис Константинович <dberman@itmo.ru>",
    "date": "Mon, 15 Dec 2025 00:40:24 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n\n \n┌─────────────────────────────\n  \n  Берман Денис Константинович, 326890\n  Университет ИТМО, ОМП\n   Председатель Совета обучающихся\n>От кого:  omp@itmo.ru\n>Кому:  dberman@itmo.ru\n>Дата: Понедельник, 15 декабря 2025, 00:36 +03:00\n> \n>ЭТО ТЕСТ НОВОЙ ФИЧИ. ИГНОРИРУЙТЕ! Здравствуйте! Прошу согласовать служебную записку во вложении.  \n>>С уважением, Берман Денис Константинович\n>>Офис молодежных про",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.238669"
  },
  "517431d2d2593925": {
    "id": "517431d2d2593925",
    "email_id": "294",
    "subject": "Согласование СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:54:59.466077",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:54:59.466210"
  },
  "dd6779c9c316d3ea": {
    "id": "dd6779c9c316d3ea",
    "email_id": "295",
    "subject": "Re: Согласование СЗ",
    "sender": "Берман Денис Константинович <dberman@itmo.ru>",
    "date": "Mon, 15 Dec 2025 00:59:22 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n\n \n┌─────────────────────────────\n  \n  Берман Денис Константинович, 326890\n  Университет ИТМО, ОМП\n   Председатель Совета обучающихся\n>От кого:  omp@itmo.ru\n>Кому:  dberman@itmo.ru\n>Дата: Понедельник, 15 декабря 2025, 00:59 +03:00\n> \n>ЭТО ТЕСТ НОВОЙ ФИЧИ. ИГНОРИРУЙТЕ! Здравствуйте! Прошу согласовать служебную записку во вложении.  \n>>С уважением, Берман Денис Константинович\n>>Офис молодежных про",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.392333"
  },
  "925aa67c2d65ccfc": {
    "id": "925aa67c2d65ccfc",
    "email_id": "296",
    "subject": "Согласование СЗ: omp@itmo.ru",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:54:59.583076",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:54:59.583226"
  },
  "d160780076d6f1a0": {
    "id": "d160780076d6f1a0",
    "email_id": "297",
    "subject": "Согласование СЗ: xlsx/СЗ_шаблон_Кй_01-01-2026_10-00-23-00(12).xlsx",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:54:59.679505",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:54:59.679687"
  },
  "418097548e3d8365": {
    "id": "418097548e3d8365",
    "email_id": "298",
    "subject": "Согласование СЗ: СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:54:59.738931",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:54:59.739109"
  },
  "a5a22683d1ae3f54": {
    "id": "a5a22683d1ae3f54",
    "email_id": "299",
    "subject": "Согласование СЗ: шаблон",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:54:59.816007",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:54:59.816171"
  },
  "e6cb12057a923426": {
    "id": "e6cb12057a923426",
    "email_id": "292",
    "subject": "Согласование СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:55:31.923966",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:55:31.924036"
  },
  "633c0a32cebc54ce": {
    "id": "633c0a32cebc54ce",
    "email_id": "294",
    "subject": "Согласование СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:55:32.062769",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:55:32.062847"
  },
  "16930ac355f72ded": {
    "id": "16930ac355f72ded",
    "email_id": "296",
    "subject": "Согласование СЗ: omp@itmo.ru",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:55:32.192654",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:55:32.192728"
  },
  "e57c798ce8fef4b2": {
    "id": "e57c798ce8fef4b2",
    "email_id": "297",
    "subject": "Согласование СЗ: xlsx/СЗ_шаблон_Кй_01-01-2026_10-00-23-00(12).xlsx",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:55:32.243394",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:55:32.243468"
  },
  "e2e847fbe6b42d12": {
    "id": "e2e847fbe6b42d12",
    "email_id": "298",
    "subject": "Согласование СЗ: СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:55:32.298293",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:55:32.298374"
  },
  "1466775ff4bdb241": {
    "id": "1466775ff4bdb241",
    "email_id": "299",
    "subject": "Согласование СЗ: шаблон",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:55:32.382676",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:55:32.382771"
  },
  "c2b0454d4ae922c2": {
    "id": "c2b0454d4ae922c2",
    "email_id": "292",
    "subject": "Согласование СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:56:05.155938",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.156031"
  },
  "e7fe738c91c4d8ad": {
    "id": "e7fe738c91c4d8ad",
    "email_id": "294",
    "subject": "Согласование СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:56:05.301635",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.302262"
  },
  "cc91ba2017d1e16f": {
    "id": "cc91ba2017d1e16f",
    "email_id": "296",
    "subject": "Согласование СЗ: omp@itmo.ru",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:56:05.469420",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.469960"
  },
  "a0d1bdee7f7d3cc2": {
    "id": "a0d1bdee7f7d3cc2",
    "email_id": "297",
    "subject": "Согласование СЗ: xlsx/СЗ_шаблон_Кй_01-01-2026_10-00-23-00(12).xlsx",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:56:05.530108",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.530184"
  },
  "964a78e4b0c7d809": {
    "id": "964a78e4b0c7d809",
    "email_id": "298",
    "subject": "Согласование СЗ: СЗ",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:56:05.599935",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.600103"
  },
  "3fa41e9e2414f0da": {
    "id": "3fa41e9e2414f0da",
    "email_id": "299",
    "subject": "Согласование СЗ: шаблон",
    "sender": "omp@itmo.ru",
    "date": "2025-12-15T02:56:05.669509",
    "body": "",
    "attachments": [],
    "received_at": "2025-12-15T02:56:05.670090"
  }
}
```

### `data/reconciliation_report.json`

```json
{
  "generated_at": "2025-12-15T02:56:05.756799",
  "reconciled_count": 0,
  "reconciled_docs": []
}
```

### `data/sent_docs.json`

```json
{}
```

### `entrypoint.sh`

```bash
#!/bin/sh
set -euo pipefail

REQ="/app/requirements.txt"
MAIN="/app/main.py"
SETUP="/app/setup.py"

if [ "${SKIP_PIP_INSTALL:-0}" != "1" ]; then
  if [ -f "$REQ" ]; then
    echo "[entrypoint] Ensuring deps..."
    python -m pip install --upgrade pip
    python -m pip install --no-cache-dir -r "$REQ"
  fi
fi

if [ -f "$MAIN" ]; then
  echo "[entrypoint] Starting ompbot..."
  python "$SETUP"
  python "$MAIN"
else
  echo "[entrypoint] No $MAIN found"; exec /bin/bash
fi

```

### `ignored.txt`

```text

```

### `main.py`

```python
# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import traceback
from utils import IgnoredList, get_secrets
from utils import VKHelper
from utils.log import *
from ompbot import *
from utils.mail_sync_worker import MailSyncManager


class Main:
    def __init__(self):
        self.token = get_secrets()['token']
        self.group_id = 204516366

        self.vk_session = vk_api.VkApi(token=self.token)
        self.VK = VKHelper(self.vk_session)

        self.info, self.error = log()
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        self.ignored = IgnoredList()
        self.metrics = Metrics()
        self.info(self.ignored.load_from_file())

        self.mail_sync = MailSyncManager()
        self.mail_sync.start(poll_interval=30)


        self.info("готов!\n")

        #handle_actions(self, actions)
    def __del__(self):
        if hasattr(self, 'mail_sync'):
            self.mail_sync.stop()
    def run(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    self.process_event(event)
            except Exception as e:
                self.error(e)
                traceback.print_exc()
                self.metrics.record_error(str(e))


    def process_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.handle_message_new(event)
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.handle_message_event(event)

    def handle_message_new(self, event):
        result = process_message_new(event, self.VK, self.ignored)
        self.handle_actions(result)

    def handle_message_event(self, event):
        result = process_message_event(event, self.VK)
        self.handle_actions(result)

    def handle_actions(self, actions):
        if not actions:
            return
        for action in actions:
            peer_id = action.get("peer_id")
            message = action.get("message", "")
            keyboard = action.get("keyboard")
            attachment = action.get("attachment")
            # message_sync = {
            #     "user_message": {"peer_id": None, "conversation_message_id": None},
            #     "manager_message": {"peer_id": None, "conversation_message_id": None}
            # }
            try:
                self.VK.send_message(peer_id, message, keyboard, attachment)
            except Exception as e:
                self.error(f"Ошибка обработки действия: {e}")


if __name__ == '__main__':
    bot = Main()
    bot.run()

```

### `ompbot.py`

```python
# -*- coding: utf-8 -*-
import json
import uuid

import requests
from datetime import datetime as date
import re
from utils import check_excel, create_excel, net_helper, mail_helper
import os
import shutil

from utils.mail_helper import MailHelper
from utils.mail_sync_worker import MailSyncManager
from utils.metrics import Metrics
from utils.user_list import UserList
from utils.mail_integration_helpers import save_sent_document, handle_admin_commands
global  admin_chat, admins, groupid
admin_chat = 1
admins = [297002785, 101822925]
groupid = 204516366

def process_message_event(event, vk_helper):
    pl = event.object.get('payload')
    user_list = UserList()
    metrics = Metrics()
    if pl:
        conversation_message_id = event.object['conversation_message_id']
        peer_id = event.object['peer_id']

        type = pl['type']
        sender = int(pl['sender'])
        if type in ['auto', 'send','approve', 'annul']:
            title = pl['title']
            tts = "Ваша служебная записка " + title
        else:
            tts=""
            title = None

        if type=='auto':
            tts += "\nпринята и отправлена на согласование!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАТЬ",
                    "payload": {"type": "approve", "sender": sender, "title": title, "isSended": True},
                    "color": "primary"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

            title = pl.get('title')
            path = pl.get('path')

            title_with_marker = f'{title}'
            # Extract club name and document name for email
            club_name_start = title_with_marker.find("/СЗ_")+4
            club_name_end = title_with_marker.find("_", club_name_start)
            club_name = title_with_marker[club_name_start:club_name_end]
            
            # Extract document name (everything after club name)
            document_name = title_with_marker[club_name_end+1:]
            if "." in document_name:
                document_name = document_name[:document_name.rfind(".")]  # Remove file extension
                
            mail = MailHelper()
            mail.send_mail(club_name, document_name, [path])

            doc_id = f"doc_{sender}"
            save_sent_document(doc_id, title_with_marker, sender, 'ITMO')
            tts = 'Письмо отправлено с маркером автосогласования'

        elif type == "send":
            tts += "\nпринята и отправлена на согласование!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАТЬ",
                    "payload": {"type": "approve", "sender": sender, "title": title, "isSended": True},
                    "color": "primary"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

        elif type == "approve":
            is_sended = pl['isSended']
            if is_sended:
                tts += "\nсогласована и внесена в систему для отображения на мониторе охраны!"
            else:
                tts += "\nсогласована и внесена в систему для получения QR на терминале!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАНО",
                    "payload": {"type": "approved", "sender": sender, "title": title, "isSended": True},
                    "color": "positive"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

            metrics.record_memo_approved(sender)

        elif type == "annul":
            by_admin = pl['byAdmin']
            managerflag = " МЕНЕДЖЕРОМ" if by_admin else ""
            tts += f" АННУЛИРОВАНА{managerflag}!"
            buttons = [
                {
                    "label": "АННУЛИРОВАНО",
                    "payload": {"type": "annuled", "sender": sender, "title": title},
                    "color": "negative"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)
        elif type=="club":
            status=pl['status']
            club=pl['club']
            if status=="decline":
                tts+="Отмена! Отправь мне служебную записку с правильным названием."
            elif status=="accept":
                tts+=f"Принято! Ты связал свой айди с клубом «{club}». Теперь отправь свою служебную записку заново"
                user_list.add(sender,club)
            keyboard = None
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)


        else:
            return
    return [{
        "peer_id": sender,
        "message": tts,
    }]


def process_message_new(event, vk_helper, ignored):
    tts = ''
    yonote = 'https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w'


    user_list = UserList()
    user_list.load_from_file()
    metrics= Metrics()


    time = int(str(date.now().time())[:2])
    weekday = date.today().weekday()
    month = int(str(date.now().date())[-5:-3])
    day = int(str(date.now().date())[-2:])
    if (month == 12 and day >= 28) or (month == 1 and day <= 8):
        tts += "С новым годом! Служебные записки не согласуются на каникулах. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только после 9 января. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif weekday > 4:
        tts += "Внимание! Служебные записки не согласуются по выходным. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только в понедельник. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif weekday == 4 and time >= 16:
        tts += "Внимание! По пятницам служебные записки не согласуются после 16:00. Вы можете отправить " \
               "документ, бот его обработает, но согласование получите только в понедельник. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif time >= 17:
        tts += "Внимание! Служебные записки не согласуются после 17:00. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только завтра. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif time < 10:
        tts += "Внимание! Служебные записки не обрабатываются до 10:00. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только в рабочее время. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"

    uid = event.message.from_id
    metrics.record_message(uid)
    peer_id = 2000000000 + uid
    msgraw = event.message.text
    msg = event.message.text.lower()
    msgs = msg.split()
    if uid > 0:
        user_get = vk_helper.vk.users.get(user_ids=uid)
        user_get = user_get[0]
        uname = user_get['first_name']
        usurname = user_get['last_name']

    if event.from_chat:
        id = event.chat_id
        uid = event.obj['message']['from_id']
        peer_id = 2000000000 + uid
        return

    else:

        if ignored.is_ignored(uid):
            if not ("менеджер" in msg or "админ" in msg):
                return

        if "менеджер" in msg or "админ" in msg:
            metrics.record_manager(uid)
            link = f"https://vk.com/gim{groupid}?sel={uid}"
            buttons = [{"label": "прямая ссылка", "payload": {"type": "userlink"}, "link": link}]
            link_keyboard = vk_helper.create_link_keyboard(buttons)
            if ignored.is_ignored(uid):
                ignored.remove(uid)
                ignored.save_to_file()
                tts = "Надеюсь, вопрос снят!"
                Сtts = f"{uname} {usurname} больше не вызывает!"
                buttons = [{"label": "ПОЗВАТЬ МЕНЕДЖЕРА", "payload": {"type": "callmanager"}, "color": "positive"}]
                keyboard = vk_helper.create_standart_keyboard(buttons)

            else:
                ignored.add(uid)
                ignored.save_to_file()
                tts = "Принято, сейчас позову! Напиши свою проблему следующим сообщением. " \
                      "Когда вопрос будет решён, ещё раз напиши команду или нажми на кнопку."
                Сtts = f"{uname} {usurname} вызывает!"
                buttons = [{"label": "СПАСИБО МЕНЕДЖЕР", "payload": {"type": "uncallmanager"}, "color": "negative"}]
                keyboard = vk_helper.create_standart_keyboard(buttons)
                metrics.record_message(uid)
            return [
                {
                    "peer_id": uid,
                    "message": tts,
                    "keyboard": keyboard,
                    "attachment": None
                },
                {
                    "peer_id": 2000000000 + admin_chat,
                    "message": Сtts,
                    "keyboard": link_keyboard,
                    "attachment": None
                }
            ]

        attachment = event.object.message['attachments']
        if not attachment:
            if vk_helper.vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid}) == 0:
                tts += "Бот создан для предобработки служебных записок в университете ИТМО и доступен только клубам. " \
                       "Поэтому чтобы иметь доступ к обработке служебных записок необходимо подписаться на это " \
                       "сообщество, ссылку ты можешь найти в еноте или спросить в группе тг!\n\nПосле подписки " \
                       "отправь ещё одно сообщение. Только в случае возникновения проблем пиши \"МЕНЕДЖЕР\""
            else:
                tts += "Отправь мне служебную записку, я проведу предпроверку. Если всё хорошо, я отправлю её на " \
                       "обработку, после чего жди сообщения от менеджера. Если возникла проблема, " \
                       "пиши \"МЕНЕДЖЕР\"\nP.S. обязательно отправляй служебные записки в формате, указанном в " \
                       "yonote: " + yonote
        if msgs:
            if uid in admins:
                if msgs[0] == "stop":
                    exit()
                elif msgs[0]=="stat":
                    tts=metrics.get_report()
                    return[{
                        "peer_id": uid,
                        "message": tts,
                    }]
                elif msgs[0] == "sender":
                    sender_type = msgs[1]
                    text = msgraw[msgraw.find("\n"):]
                    tts = f"Готово. Проверь текст и отправляй рассылку {sender_type}:\n\n{text}"
                    buttons = [{"label": "ОТПРАВИТЬ РАССЫЛКУ",
                                "payload": {"type": "sender", "sender": sender_type, "text": text}, "color": "primary"}]
                    keyboard = vk_helper.create_keyboard(buttons)
                    return [{
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": keyboard
                    }]
                elif msgs[0]=="sync":
                    mail_sync = MailSyncManager()
                    result = mail_sync.force_sync()

                    if result['status'] == 'success':
                        tts = "Синхронизация почты выполнена."
                    else:
                        tts = f"Ошибка синхронизации: {result['message']}"
                    return[{
                        "peer_id": uid,
                        "message": tts,
                    }]
                if msgs[0] == "mailstat":
                    mail_sync = MailSyncManager()
                    metrics = mail_sync.get_metrics()

                    tts = (
                        f"Метрики почты:\n"
                        f"Получено писем: {metrics.get('emails_received', 0)}\n"
                        f"Согласовано документов: {metrics.get('documents_reconciled', 0)}\n"
                        f"Ошибок: {metrics.get('reconciliation_failed', 0)}\n"
                        f"Последняя проверка: {metrics.get('last_check', 'Never')}"
                    )
                    return[{
                        "peer_id": uid,
                        "message": tts,
                    }]
        attachment = event.object.message['attachments']
        if attachment:
            attachment = attachment[0]
            attachment = attachment['doc'] if attachment['type'] == 'doc' else None
            attachment_title = attachment['title']
            attachment_ext = attachment['ext']

            attachment_url = attachment['url']
            if (not (re.match(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title))) or (
                    "шаблон" in attachment_title and uid not in admins):
                tts += "ошибка в названии файла. пример:\nСЗ_шаблон.xlsx\nдопускается:\nСЗ_шаблон.метаинф.xlsx\n" \
                       "Вместо \"шаблон\" везде одинаковое название клуба (без пробелов, лучше латиницей)."
                return [{
                    "peer_id": uid,
                    "message": tts,
                }]
            attachment_title = re.search(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title).group()[3:]
            club_name=attachment_title[:-1]


            if club_name not in user_list.get_clubs(uid):
                tts+=f"Вы хотите связать свой аккаунт с клубом «{club_name}». В дальнейшем используйте одно название для всех СЗ_название от одного клуба.\n\nНажимая кнопку ПОДТВЕРДИТЬ и продолжая пользоваться сервисом вы соглашаетесь с правилами пользования и подтверждаете, что:\n1) данные в записках корректны и принадлежат реальным людям;\n2) знаете, что клубы обязаны следить за своими гостями на территории университета, в частности не допускать их самостоятельного нахождения на территории вне мероприятия;\n3) ознакомлены с графиком работы бота: пн-чт 10:00-17:00, пт 10:00-16:00. В остальное время записки не обрабатываются, так как не работает ни УФБ, ни ОМП;\n4) знаете, где взять информацию о формате СЗ и командах бота: https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w. \n\nВ случае нарушений этих простых правил, клубу может быть полностью ограничен доступ к сервису."
                buttons = [
                    {"label": "ПОДТВЕРДИТЬ", "payload": {"type": "club",'sender': uid, "status":"accept","club":club_name}, "color": "positive"},
                    {"label": "ОТМЕНИТЬ", "payload": {"type": "club",'sender': uid,"status":"decline","club":club_name}, "color": "negative"}
                ]
                keyboard = vk_helper.create_keyboard(buttons)
                return [{
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": keyboard
                    }]

            path = net_helper.attachment_extract(attachment_url, club_name, attachment_ext)
            if attachment_ext in ['xlsx', 'docx']:
                metrics.record_memo_received(uid)
                if attachment_ext == 'xlsx':
                    try:
                        check = check_excel(path)
                    except Exception as exc:
                        check = ["ER", exc]
                    if check[0] == "success":
                        rows = check[1]
                        kolgost = int(float(rows[-1][0]))
                        korpus = rows[0][1]
                        data = rows[0][3]
                        merotitle = rows[0][5]
                        org = rows[1][7]
                        orgnomer = str(rows[2][7])

                        newname = "СЗ_" + attachment_title[:attachment_title.find(".")] + "_"+korpus[0]+korpus[-1]+"_" + "_".join(
                            rows[0][3].replace(":", "-").replace(".", "-").split())
                        newpath = "data/xlsx/" + newname + ".xlsx"
                        for _ in range(1, 999):
                            if os.path.exists(newpath):
                                base_name = newname[:newname.rfind("(")] if "(" in newname else newname
                                newname = f"{base_name}({_})"
                                newpath = "data/xlsx/" + newname + ".xlsx"
                            else:
                                break

                        create_excel(newpath, rows)

                        result = json.loads(requests.post(
                            vk_helper.vk.docs.getMessagesUploadServer(type='doc',
                                                                      peer_id=event.object.message['peer_id'])[
                                'upload_url'],
                            files={'file': open(newpath, 'rb')}).text)
                        jsonAnswer = vk_helper.vk.docs.save(file=result['file'], title=newname, tags=[])
                        attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"


                        tts += f"Принято! Отправил на проверку, ожидайте ответа.\nПроверьте данные. В случае несовпадений, вызовите менеджера: \nДата: {data}\nорганизатор: {org} (+{orgnomer})" \
                               f"\nНазвание мероприятия: {merotitle}\nКорпус: {korpus} \nКоличество гостей:  {kolgost}"
                        Сtts = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nдата: {data}\nорганизатор: {org} (+{orgnomer})" \
                               f"\nколичество гостей:  {kolgost}\nназвание мероприятия: {merotitle}\nкорпус: {korpus} \nотправитель: {uname} {usurname}"
                        newname = newpath[5:]
                    else:
                        if check[0] == "00":
                            tts += "ошибка в одной из ячеек, которые нельзя менять." \
                                " перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону"
                        elif check[0] == "01":
                            tts += "ошибка в одной из ячеек, которые необходимо было изменить. поменяйте шаблон!"
                        elif check[0] == "02":
                            tts += "дата не может быть ранее сегодняшней!"
                        elif check[0] == "ER":
                            tts += "неопознанная ошибка, позовите менеджера: " + str(check[1])
                        else:
                            tts += "ошибка в ячейке " + check
                        metrics.record_memo_filtered(uid)
                        return [{
                            "peer_id": uid,
                            "message": tts,
                        }]
                elif attachment_ext=='docx':
                    newname = "СЗ_" + attachment_title[:attachment_title.find(".")]+"_" + "_".join(str(date.now())[:-7].replace(":", "-").split())
                    newpath = "data/docx/" + newname + ".docx"
                    for _ in range(1, 999):
                        if os.path.exists(newpath):
                            base_name = newname[:newname.rfind("(")] if "(" in newname else newname
                            newname = f"{base_name}({_})"
                            newpath = "data/docx/" + newname + ".docx"
                        else: break
                    shutil.copy(path, newpath)
                    result = json.loads(requests.post(
                        vk_helper.vk.docs.getMessagesUploadServer(type='doc',
                                                                  peer_id=event.object.message['peer_id'])[
                            'upload_url'],
                        files={'file': open(newpath, 'rb')}).text)
                    jsonAnswer = vk_helper.vk.docs.save(file=result['file'], title=newname, tags=[])
                    attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"

                    tts += f"Принято! Отправил на проверку, ожидайте ответа.\n"
                    Сtts = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nотправитель: {uname} {usurname}"
                    newname = newname+".docx"
                else:
                    pass
                buttons = [
                    {
                        "label": "АВТОСОГЛАСОВАНИЕ",
                        "payload": {"type": "auto", 'sender': uid, 'title': newname, 'path': newpath},
                        "color": "secondary"
                    },
                    {
                        "label": "ОТПРАВИТЬ",
                        "payload": {"type": "send", 'sender': uid, 'title': newname},
                        "color": "primary",
                        "newline": True
                    },
                    {
                        "label": "СОГЛАСОВАТЬ",
                        "payload": {"type": "approve", 'sender': uid, 'title': newname, 'isSended': False},
                        "color": "primary"
                    },
                    {
                        "label": "АННУЛИРОВАТЬ",
                        "payload": {"type": "annul", 'sender': uid, 'title': newname, 'byAdmin': True},
                        "color": "negative",
                        "newline": True
                    }
                ]
                Ckeyboard = vk_helper.create_keyboard(buttons)

                # buttons = [{"label": "ОТМЕНИТЬ", "payload": {"type": "annul", 'sender': uid, 'title': newpath, 'byAdmin': False}, "color": "secondary"}]
                # keyboard = vk_helper.create_keyboard(buttons)
                # todo: сделать синхронизацию, чтобы можно было отменять со стороны пользователя
                return [
                    {
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": None,
                        "attachment": attachment
                    },
                    {
                        "peer_id": 2000000000 + admin_chat,
                        "message": Сtts,
                        "keyboard": Ckeyboard,
                        "attachment": attachment
                    }
                ]
        metrics.record_memo_filtered(uid)
        return [{
            "peer_id": uid,
            "message": tts,
        }]

```

### `project_analysis.md`

```markdown
# Анализ проекта

**Папка**: `ompbot`

## 📁 Структура

```
.env (265B)
.github/workflows/deploy.yml (2.2KB)
.gitignore (62B)
Dockerfile (623B)
README.md (657B)
data/metrics.yaml (6.8KB)
data/py.log (35.9KB)
data/received_docs.json (20.8KB)
data/reconciliation_report.json (100B)
data/sent_docs.json (2B)
entrypoint.sh (472B)
ignored.txt (0B)
main.py (2.6KB)
ompbot.py (25.8KB)
project_analysis.md (0B)
project_to_text.py (3.4KB)
requirements.txt (60B)
setup.py (904B)
test_mail_helper.py (1.1KB)
test_mail_helper_simple.py (1.1KB)
users.yml (0B)
utils/__init__.py (439B)
utils/__init__.pyc (570B)
utils/excel_helper.py (6.3KB)
utils/ignored_list.py (1.6KB)
utils/log.py (664B)
utils/mail_helper.py (4.2KB)
utils/mail_integration_helpers.py (2.0KB)
utils/mail_poller.py (1.5KB)
utils/mail_reciever.py (10.7KB)
utils/mail_sync_worker.py (3.8KB)
utils/metrics.py (4.1KB)
utils/net_helper.py (535B)
utils/user_list.py (2.8KB)
utils/vk_helper.py (6.2KB)
```

## 📄 Исходный код

### `.github/workflows/deploy.yml`

```yaml
name: Deploy on Push

on:
  push:
    branches: [ master, dev ]
  pull_request:
    branches: [ master, dev ]

permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
  
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install flake8
          pip install -r requirements.txt
  
      - name: Run linter - hard errors only
        run: |
          flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Run linter - soft style guide
        run: |
          flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
  build-and-push:
    if: github.event_name == 'push' && github.ref == 'refs/heads/master'
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR (via PAT)
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: 'enderdissa'
          password: ${{ secrets.GHCR_PUSH_TOKEN }}
      - name: Build & Tag
        run: |
          OWNER=$(echo "${{ github.repository_owner }}" | tr '[:upper:]' '[:lower:]')
          IMAGE="ghcr.io/${OWNER}/ompbot"
          docker build -t $IMAGE:latest -f ./Dockerfile .
          docker tag $IMAGE:latest $IMAGE:${{ github.run_number }}
          echo "IMAGE=$IMAGE" >> $GITHUB_ENV
      - name: Push
        run: |
          docker push $IMAGE:latest
          docker push $IMAGE:${{ github.run_number }}
  # deploy:
  #     needs: test
  #     runs-on: ubuntu-latest
  #     steps:
  #       - name: Execute SSH Commands
  #         uses: GPTED/SSH-My-Action@0.1
  #         with:
  #           HOST: 45.93.200.157
  #           USER: bot_dev
  #           PORT: 22
  #           PRIVATE_KEY: ${{ secrets.BOT_DEV_SSH_PRIVATE_KEY }}
  #           CMD: |
  #             cd /srv/bots/vk-ompbot/app/ompbot;
  #             git reset --hard HEAD;
  #             git pull;
  #             cd /srv/bots/vk-ompbot;
  #             docker compose up -d --build --force-recreate;

```

### `.gitignore`

```text
.idea/*
token.txt
ignored.txt
*.xlsx
*.docx
*.log
*.yml
*.yaml
```

### `Dockerfile`

```text
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential gcc ca-certificates \
  && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash bot \
  && mkdir -p /app && chown bot:bot /app

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
  && pip install --no-cache-dir -r /app/requirements.txt

COPY . /app
RUN chown -R bot:bot /app
RUN chmod +x /app/entrypoint.sh

USER bot
WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]

```

### `README.md`

```markdown
# ompbot
![Static Badge](https://img.shields.io/badge/EnderDissa-ompbot-ompbot)
![GitHub top language](https://img.shields.io/github/languages/top/EnderDissa/ompbot)


HOWTO:
1) git clone
2) pip install -r ./requirements.py (installing requirements)
3) python setup.py (created neccesarry dirs and files, asking for token)
4) python main.py (running bot itself)

Рекомендую добавить ompbot.py в параметры автозапуска и настроить параметры энергосбережения (на рабочем ПК) или запустить создать ../compose.yml (на нормальном сервере)


```

### `data/metrics.yaml`

```yaml
errors: 61
history:
- event: error
  timestamp: '2025-12-15T02:56:22.730169'
  trigger: 'HTTPSConnectionPool(host=''lp.vk.com'', port=443): Read timed out. (read
    timeout=35)'
- event: error
  timestamp: '2025-12-15T02:56:22.941553'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.044912'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.181175'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.284652'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.390311'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.501468'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.612478'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.724475'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.859483'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:23.992722'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.101742'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.248581'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.411370'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.549754'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.710115'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:24.872071'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.010813'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.163192'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.336478'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.529007'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.653380'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:25.789061'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.034605'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.238364'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.382184'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.539105'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.678190'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.816852'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:26.980272'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.109196'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.239990'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.375283'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.544715'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.706780'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:27.885789'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.028567'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.165504'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.335332'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.482787'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.620418'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.788303'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:28.917986'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.068099'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.214737'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.383542'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.534822'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.696020'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:29.847950'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.000148'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.159784'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.313671'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.474937'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.616078'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.762823'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:30.909967'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.078591'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.274205'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.444006'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.587128'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
- event: error
  timestamp: '2025-12-15T02:56:31.768939'
  trigger: 'Expecting value: line 1 column 1 (char 0)'
manager: 0
memo_approved: 0
memo_filtered: 0
memo_received: 0
message: 0

```

### `data/received_docs.json`

```json
{
  "7f4669b6526b45cb": {
    "id": "7f4669b6526b45cb",
    "email_id": "280",
    "subject": "Re: Согласование СЗ",
    "sender": "УФБ <pass@itmo.ru>",
    "date": "Mon, 08 Dec 2025 12:42:47 +0300",
    "body": "\nДобрый день!\n \nСлужебные записки согласованы и внесены в систему для отображения на мониторе охраны.\n \n \n\n \n \nС уважением,  Управление Физической Безопасности\nтел.:  +7 (812) 480-20-10 , доб. 2102 или 2101  |  pass@itmo.ru  \n         +7 (812) 607-04-16 , доб. 20 или 22\n\nУниверситет ИТМО | ITMO University \nКронверкский пр., 49, каб. 1105. Санкт-Петербург, Россия, 197101 | Kronverksky pr., 49, office. 1105. Saint Petersburg, Russia, 197101\n\nwww.ifmo.ru  \n>От кого: Офис молодежных проектов ИТМО < ",
    "attachments": [],
    "received_at": "2025-12-15T02:56:03.067365"
  },

}
```

### `data/reconciliation_report.json`

```json
{
  "generated_at": "2025-12-15T02:56:05.756799",
  "reconciled_count": 0,
  "reconciled_docs": []
}
```

### `data/sent_docs.json`

```json
{}
```

### `entrypoint.sh`

```bash
#!/bin/sh
set -euo pipefail

REQ="/app/requirements.txt"
MAIN="/app/main.py"
SETUP="/app/setup.py"

if [ "${SKIP_PIP_INSTALL:-0}" != "1" ]; then
  if [ -f "$REQ" ]; then
    echo "[entrypoint] Ensuring deps..."
    python -m pip install --upgrade pip
    python -m pip install --no-cache-dir -r "$REQ"
  fi
fi

if [ -f "$MAIN" ]; then
  echo "[entrypoint] Starting ompbot..."
  python "$SETUP"
  python "$MAIN"
else
  echo "[entrypoint] No $MAIN found"; exec /bin/bash
fi

```

### `ignored.txt`

```text

```

### `main.py`

```python
# -*- coding: utf-8 -*-
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import traceback
from utils import IgnoredList, get_secrets
from utils import VKHelper
from utils.log import *
from ompbot import *
from utils.mail_sync_worker import MailSyncManager


class Main:
    def __init__(self):
        self.token = get_secrets()['token']
        self.group_id = 204516366

        self.vk_session = vk_api.VkApi(token=self.token)
        self.VK = VKHelper(self.vk_session)

        self.info, self.error = log()
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        self.ignored = IgnoredList()
        self.metrics = Metrics()
        self.info(self.ignored.load_from_file())

        self.mail_sync = MailSyncManager()
        self.mail_sync.start(poll_interval=30)


        self.info("готов!\n")

        #handle_actions(self, actions)
    def __del__(self):
        if hasattr(self, 'mail_sync'):
            self.mail_sync.stop()
    def run(self):
        while True:
            try:
                for event in self.longpoll.listen():
                    self.process_event(event)
            except Exception as e:
                self.error(e)
                traceback.print_exc()
                self.metrics.record_error(str(e))


    def process_event(self, event):
        if event.type == VkBotEventType.MESSAGE_NEW:
            self.handle_message_new(event)
        elif event.type == VkBotEventType.MESSAGE_EVENT:
            self.handle_message_event(event)

    def handle_message_new(self, event):
        result = process_message_new(event, self.VK, self.ignored)
        self.handle_actions(result)

    def handle_message_event(self, event):
        result = process_message_event(event, self.VK)
        self.handle_actions(result)

    def handle_actions(self, actions):
        if not actions:
            return
        for action in actions:
            peer_id = action.get("peer_id")
            message = action.get("message", "")
            keyboard = action.get("keyboard")
            attachment = action.get("attachment")
            # message_sync = {
            #     "user_message": {"peer_id": None, "conversation_message_id": None},
            #     "manager_message": {"peer_id": None, "conversation_message_id": None}
            # }
            try:
                self.VK.send_message(peer_id, message, keyboard, attachment)
            except Exception as e:
                self.error(f"Ошибка обработки действия: {e}")


if __name__ == '__main__':
    bot = Main()
    bot.run()

```

### `ompbot.py`

```python
# -*- coding: utf-8 -*-
import json
import uuid

import requests
from datetime import datetime as date
import re
from utils import check_excel, create_excel, net_helper, mail_helper
import os
import shutil

from utils.mail_helper import MailHelper
from utils.mail_sync_worker import MailSyncManager
from utils.metrics import Metrics
from utils.user_list import UserList
from utils.mail_integration_helpers import save_sent_document, handle_admin_commands
global  admin_chat, admins, groupid
admin_chat = 1
admins = [297002785, 101822925]
groupid = 204516366

def process_message_event(event, vk_helper):
    pl = event.object.get('payload')
    user_list = UserList()
    metrics = Metrics()
    if pl:
        conversation_message_id = event.object['conversation_message_id']
        peer_id = event.object['peer_id']

        type = pl['type']
        sender = int(pl['sender'])
        if type in ['auto', 'send','approve', 'annul']:
            title = pl['title']
            tts = "Ваша служебная записка " + title
        else:
            tts=""
            title = None

        if type=='auto':
            tts += "\nпринята и отправлена на согласование!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАТЬ",
                    "payload": {"type": "approve", "sender": sender, "title": title, "isSended": True},
                    "color": "primary"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

            title = pl.get('title')
            path = pl.get('path')

            title_with_marker = f'{title}'
            # Extract club name and document name for email
            club_name_start = title_with_marker.find("/СЗ_")+4
            club_name_end = title_with_marker.find("_", club_name_start)
            club_name = title_with_marker[club_name_start:club_name_end]
            
            # Extract document name (everything after club name)
            document_name = title_with_marker[club_name_end+1:]
            if "." in document_name:
                document_name = document_name[:document_name.rfind(".")]  # Remove file extension
                
            mail = MailHelper()
            mail.send_mail(club_name, document_name, [path])

            doc_id = f"doc_{sender}"
            save_sent_document(doc_id, title_with_marker, sender, 'ITMO')
            tts = 'Письмо отправлено с маркером автосогласования'

        elif type == "send":
            tts += "\nпринята и отправлена на согласование!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАТЬ",
                    "payload": {"type": "approve", "sender": sender, "title": title, "isSended": True},
                    "color": "primary"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

        elif type == "approve":
            is_sended = pl['isSended']
            if is_sended:
                tts += "\nсогласована и внесена в систему для отображения на мониторе охраны!"
            else:
                tts += "\nсогласована и внесена в систему для получения QR на терминале!"
            buttons = [
                {
                    "label": "ОТПРАВЛЕНО",
                    "payload": {"type": "sended", "sender": sender, "title": title},
                    "color": "positive"
                },
                {
                    "label": "СОГЛАСОВАНО",
                    "payload": {"type": "approved", "sender": sender, "title": title, "isSended": True},
                    "color": "positive"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)

            metrics.record_memo_approved(sender)

        elif type == "annul":
            by_admin = pl['byAdmin']
            managerflag = " МЕНЕДЖЕРОМ" if by_admin else ""
            tts += f" АННУЛИРОВАНА{managerflag}!"
            buttons = [
                {
                    "label": "АННУЛИРОВАНО",
                    "payload": {"type": "annuled", "sender": sender, "title": title},
                    "color": "negative"
                }
            ]
            keyboard = vk_helper.create_keyboard(buttons)
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)
        elif type=="club":
            status=pl['status']
            club=pl['club']
            if status=="decline":
                tts+="Отмена! Отправь мне служебную записку с правильным названием."
            elif status=="accept":
                tts+=f"Принято! Ты связал свой айди с клубом «{club}». Теперь отправь свою служебную записку заново"
                user_list.add(sender,club)
            keyboard = None
            vk_helper.edit_keyboard(peer_id, conversation_message_id, keyboard)


        else:
            return
    return [{
        "peer_id": sender,
        "message": tts,
    }]


def process_message_new(event, vk_helper, ignored):
    tts = ''
    yonote = 'https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w'


    user_list = UserList()
    user_list.load_from_file()
    metrics= Metrics()


    time = int(str(date.now().time())[:2])
    weekday = date.today().weekday()
    month = int(str(date.now().date())[-5:-3])
    day = int(str(date.now().date())[-2:])
    if (month == 12 and day >= 28) or (month == 1 and day <= 8):
        tts += "С новым годом! Служебные записки не согласуются на каникулах. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только после 9 января. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif weekday > 4:
        tts += "Внимание! Служебные записки не согласуются по выходным. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только в понедельник. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif weekday == 4 and time >= 16:
        tts += "Внимание! По пятницам служебные записки не согласуются после 16:00. Вы можете отправить " \
               "документ, бот его обработает, но согласование получите только в понедельник. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif time >= 17:
        tts += "Внимание! Служебные записки не согласуются после 17:00. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только завтра. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"
    elif time < 10:
        tts += "Внимание! Служебные записки не обрабатываются до 10:00. Вы можете отправить документ, " \
               "бот его обработает, но согласование получите только в рабочее время. Если " \
               "ситуация срочная, пишите \"МЕНЕДЖЕР\"\n\n"

    uid = event.message.from_id
    metrics.record_message(uid)
    peer_id = 2000000000 + uid
    msgraw = event.message.text
    msg = event.message.text.lower()
    msgs = msg.split()
    if uid > 0:
        user_get = vk_helper.vk.users.get(user_ids=uid)
        user_get = user_get[0]
        uname = user_get['first_name']
        usurname = user_get['last_name']

    if event.from_chat:
        id = event.chat_id
        uid = event.obj['message']['from_id']
        peer_id = 2000000000 + uid
        return

    else:

        if ignored.is_ignored(uid):
            if not ("менеджер" in msg or "админ" in msg):
                return

        if "менеджер" in msg or "админ" in msg:
            metrics.record_manager(uid)
            link = f"https://vk.com/gim{groupid}?sel={uid}"
            buttons = [{"label": "прямая ссылка", "payload": {"type": "userlink"}, "link": link}]
            link_keyboard = vk_helper.create_link_keyboard(buttons)
            if ignored.is_ignored(uid):
                ignored.remove(uid)
                ignored.save_to_file()
                tts = "Надеюсь, вопрос снят!"
                Сtts = f"{uname} {usurname} больше не вызывает!"
                buttons = [{"label": "ПОЗВАТЬ МЕНЕДЖЕРА", "payload": {"type": "callmanager"}, "color": "positive"}]
                keyboard = vk_helper.create_standart_keyboard(buttons)

            else:
                ignored.add(uid)
                ignored.save_to_file()
                tts = "Принято, сейчас позову! Напиши свою проблему следующим сообщением. " \
                      "Когда вопрос будет решён, ещё раз напиши команду или нажми на кнопку."
                Сtts = f"{uname} {usurname} вызывает!"
                buttons = [{"label": "СПАСИБО МЕНЕДЖЕР", "payload": {"type": "uncallmanager"}, "color": "negative"}]
                keyboard = vk_helper.create_standart_keyboard(buttons)
                metrics.record_message(uid)
            return [
                {
                    "peer_id": uid,
                    "message": tts,
                    "keyboard": keyboard,
                    "attachment": None
                },
                {
                    "peer_id": 2000000000 + admin_chat,
                    "message": Сtts,
                    "keyboard": link_keyboard,
                    "attachment": None
                }
            ]

        attachment = event.object.message['attachments']
        if not attachment:
            if vk_helper.vk_session.method('groups.isMember', {'group_id': groupid, 'user_id': uid}) == 0:
                tts += "Бот создан для предобработки служебных записок в университете ИТМО и доступен только клубам. " \
                       "Поэтому чтобы иметь доступ к обработке служебных записок необходимо подписаться на это " \
                       "сообщество, ссылку ты можешь найти в еноте или спросить в группе тг!\n\nПосле подписки " \
                       "отправь ещё одно сообщение. Только в случае возникновения проблем пиши \"МЕНЕДЖЕР\""
            else:
                tts += "Отправь мне служебную записку, я проведу предпроверку. Если всё хорошо, я отправлю её на " \
                       "обработку, после чего жди сообщения от менеджера. Если возникла проблема, " \
                       "пиши \"МЕНЕДЖЕР\"\nP.S. обязательно отправляй служебные записки в формате, указанном в " \
                       "yonote: " + yonote
        if msgs:
            if uid in admins:
                if msgs[0] == "stop":
                    exit()
                elif msgs[0]=="stat":
                    tts=metrics.get_report()
                    return[{
                        "peer_id": uid,
                        "message": tts,
                    }]
                elif msgs[0] == "sender":
                    sender_type = msgs[1]
                    text = msgraw[msgraw.find("\n"):]
                    tts = f"Готово. Проверь текст и отправляй рассылку {sender_type}:\n\n{text}"
                    buttons = [{"label": "ОТПРАВИТЬ РАССЫЛКУ",
                                "payload": {"type": "sender", "sender": sender_type, "text": text}, "color": "primary"}]
                    keyboard = vk_helper.create_keyboard(buttons)
                    return [{
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": keyboard
                    }]
                elif msgs[0]=="sync":
                    mail_sync = MailSyncManager()
                    result = mail_sync.force_sync()

                    if result['status'] == 'success':
                        tts = "Синхронизация почты выполнена."
                    else:
                        tts = f"Ошибка синхронизации: {result['message']}"
                    return[{
                        "peer_id": uid,
                        "message": tts,
                    }]
                if msgs[0] == "mailstat":
                    mail_sync = MailSyncManager()
                    metrics = mail_sync.get_metrics()

                    tts = (
                        f"Метрики почты:\n"
                        f"Получено писем: {metrics.get('emails_received', 0)}\n"
                        f"Согласовано документов: {metrics.get('documents_reconciled', 0)}\n"
                        f"Ошибок: {metrics.get('reconciliation_failed', 0)}\n"
                        f"Последняя проверка: {metrics.get('last_check', 'Never')}"
                    )
                    return[{
                        "peer_id": uid,
                        "message": tts,
                    }]
        attachment = event.object.message['attachments']
        if attachment:
            attachment = attachment[0]
            attachment = attachment['doc'] if attachment['type'] == 'doc' else None
            attachment_title = attachment['title']
            attachment_ext = attachment['ext']

            attachment_url = attachment['url']
            if (not (re.match(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title))) or (
                    "шаблон" in attachment_title and uid not in admins):
                tts += "ошибка в названии файла. пример:\nСЗ_шаблон.xlsx\nдопускается:\nСЗ_шаблон.метаинф.xlsx\n" \
                       "Вместо \"шаблон\" везде одинаковое название клуба (без пробелов, лучше латиницей)."
                return [{
                    "peer_id": uid,
                    "message": tts,
                }]
            attachment_title = re.search(r'СЗ_[а-яёА-ЯЁa-zA-Z]+\.', attachment_title).group()[3:]
            club_name=attachment_title[:-1]


            if club_name not in user_list.get_clubs(uid):
                tts+=f"Вы хотите связать свой аккаунт с клубом «{club_name}». В дальнейшем используйте одно название для всех СЗ_название от одного клуба.\n\nНажимая кнопку ПОДТВЕРДИТЬ и продолжая пользоваться сервисом вы соглашаетесь с правилами пользования и подтверждаете, что:\n1) данные в записках корректны и принадлежат реальным людям;\n2) знаете, что клубы обязаны следить за своими гостями на территории университета, в частности не допускать их самостоятельного нахождения на территории вне мероприятия;\n3) ознакомлены с графиком работы бота: пн-чт 10:00-17:00, пт 10:00-16:00. В остальное время записки не обрабатываются, так как не работает ни УФБ, ни ОМП;\n4) знаете, где взять информацию о формате СЗ и командах бота: https://ursi.yonote.ru/share/clubs/doc/sluzhebnye-zapiski-i-prohod-gostej-bihQHvmk8w. \n\nВ случае нарушений этих простых правил, клубу может быть полностью ограничен доступ к сервису."
                buttons = [
                    {"label": "ПОДТВЕРДИТЬ", "payload": {"type": "club",'sender': uid, "status":"accept","club":club_name}, "color": "positive"},
                    {"label": "ОТМЕНИТЬ", "payload": {"type": "club",'sender': uid,"status":"decline","club":club_name}, "color": "negative"}
                ]
                keyboard = vk_helper.create_keyboard(buttons)
                return [{
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": keyboard
                    }]

            path = net_helper.attachment_extract(attachment_url, club_name, attachment_ext)
            if attachment_ext in ['xlsx', 'docx']:
                metrics.record_memo_received(uid)
                if attachment_ext == 'xlsx':
                    try:
                        check = check_excel(path)
                    except Exception as exc:
                        check = ["ER", exc]
                    if check[0] == "success":
                        rows = check[1]
                        kolgost = int(float(rows[-1][0]))
                        korpus = rows[0][1]
                        data = rows[0][3]
                        merotitle = rows[0][5]
                        org = rows[1][7]
                        orgnomer = str(rows[2][7])

                        newname = "СЗ_" + attachment_title[:attachment_title.find(".")] + "_"+korpus[0]+korpus[-1]+"_" + "_".join(
                            rows[0][3].replace(":", "-").replace(".", "-").split())
                        newpath = "data/xlsx/" + newname + ".xlsx"
                        for _ in range(1, 999):
                            if os.path.exists(newpath):
                                base_name = newname[:newname.rfind("(")] if "(" in newname else newname
                                newname = f"{base_name}({_})"
                                newpath = "data/xlsx/" + newname + ".xlsx"
                            else:
                                break

                        create_excel(newpath, rows)

                        result = json.loads(requests.post(
                            vk_helper.vk.docs.getMessagesUploadServer(type='doc',
                                                                      peer_id=event.object.message['peer_id'])[
                                'upload_url'],
                            files={'file': open(newpath, 'rb')}).text)
                        jsonAnswer = vk_helper.vk.docs.save(file=result['file'], title=newname, tags=[])
                        attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"


                        tts += f"Принято! Отправил на проверку, ожидайте ответа.\nПроверьте данные. В случае несовпадений, вызовите менеджера: \nДата: {data}\nорганизатор: {org} (+{orgnomer})" \
                               f"\nНазвание мероприятия: {merotitle}\nКорпус: {korpus} \nКоличество гостей:  {kolgost}"
                        Сtts = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nдата: {data}\nорганизатор: {org} (+{orgnomer})" \
                               f"\nколичество гостей:  {kolgost}\nназвание мероприятия: {merotitle}\nкорпус: {korpus} \nотправитель: {uname} {usurname}"
                        newname = newpath[5:]
                    else:
                        if check[0] == "00":
                            tts += "ошибка в одной из ячеек, которые нельзя менять." \
                                " перепроверьте A1, A2, B2, C1, C2, D2, E1, E2, F2, G1, G2, G3, H1 по шаблону"
                        elif check[0] == "01":
                            tts += "ошибка в одной из ячеек, которые необходимо было изменить. поменяйте шаблон!"
                        elif check[0] == "02":
                            tts += "дата не может быть ранее сегодняшней!"
                        elif check[0] == "ER":
                            tts += "неопознанная ошибка, позовите менеджера: " + str(check[1])
                        else:
                            tts += "ошибка в ячейке " + check
                        metrics.record_memo_filtered(uid)
                        return [{
                            "peer_id": uid,
                            "message": tts,
                        }]
                elif attachment_ext=='docx':
                    newname = "СЗ_" + attachment_title[:attachment_title.find(".")]+"_" + "_".join(str(date.now())[:-7].replace(":", "-").split())
                    newpath = "data/docx/" + newname + ".docx"
                    for _ in range(1, 999):
                        if os.path.exists(newpath):
                            base_name = newname[:newname.rfind("(")] if "(" in newname else newname
                            newname = f"{base_name}({_})"
                            newpath = "data/docx/" + newname + ".docx"
                        else: break
                    shutil.copy(path, newpath)
                    result = json.loads(requests.post(
                        vk_helper.vk.docs.getMessagesUploadServer(type='doc',
                                                                  peer_id=event.object.message['peer_id'])[
                            'upload_url'],
                        files={'file': open(newpath, 'rb')}).text)
                    jsonAnswer = vk_helper.vk.docs.save(file=result['file'], title=newname, tags=[])
                    attachment = f"doc{jsonAnswer['doc']['owner_id']}_{jsonAnswer['doc']['id']}"

                    tts += f"Принято! Отправил на проверку, ожидайте ответа.\n"
                    Сtts = f"новая проходка: vk.com/gim{groupid}?sel={uid}\nотправитель: {uname} {usurname}"
                    newname = newname+".docx"
                else:
                    pass
                buttons = [
                    {
                        "label": "АВТОСОГЛАСОВАНИЕ",
                        "payload": {"type": "auto", 'sender': uid, 'title': newname, 'path': newpath},
                        "color": "secondary"
                    },
                    {
                        "label": "ОТПРАВИТЬ",
                        "payload": {"type": "send", 'sender': uid, 'title': newname},
                        "color": "primary",
                        "newline": True
                    },
                    {
                        "label": "СОГЛАСОВАТЬ",
                        "payload": {"type": "approve", 'sender': uid, 'title': newname, 'isSended': False},
                        "color": "primary"
                    },
                    {
                        "label": "АННУЛИРОВАТЬ",
                        "payload": {"type": "annul", 'sender': uid, 'title': newname, 'byAdmin': True},
                        "color": "negative",
                        "newline": True
                    }
                ]
                Ckeyboard = vk_helper.create_keyboard(buttons)

                # buttons = [{"label": "ОТМЕНИТЬ", "payload": {"type": "annul", 'sender': uid, 'title': newpath, 'byAdmin': False}, "color": "secondary"}]
                # keyboard = vk_helper.create_keyboard(buttons)
                # todo: сделать синхронизацию, чтобы можно было отменять со стороны пользователя
                return [
                    {
                        "peer_id": uid,
                        "message": tts,
                        "keyboard": None,
                        "attachment": attachment
                    },
                    {
                        "peer_id": 2000000000 + admin_chat,
                        "message": Сtts,
                        "keyboard": Ckeyboard,
                        "attachment": attachment
                    }
                ]
        metrics.record_memo_filtered(uid)
        return [{
            "peer_id": uid,
            "message": tts,
        }]

```

### `project_to_text.py`

```python
"""
Простой скрипт для анализа текущего репозитория
Запуск: python analyze.py (из корня проекта)
"""

import os
from pathlib import Path

# Исключаемые директории
EXCLUDE_DIRS = {'.git', '__pycache__', '.pytest_cache', 'venv', '.venv',
                'node_modules', '.idea', '.vscode', '.egg-info', 'dist', 'build', '.env'}
EXCLUDE_FILES = {'.pyc', '.pyo', '.so', '.exe', '.dll'}

def scan_directory(path, output_file):
    """Сканирует директорию и сохраняет файлы в markdown"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# Анализ проекта\n\n")
        f.write(f"**Папка**: `{Path(path).name}`\n\n")

        # Собираем всё дерево
        all_files = []
        for root, dirs, files in os.walk(path):
            # Исключаем директории
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, path)
                all_files.append((filepath, rel_path))

        # Структура файлов
        f.write("## 📁 Структура\n\n```\n")
        for filepath, rel_path in sorted(all_files):
            try:
                size = os.path.getsize(filepath)
                size_str = f"{size/1024:.1f}KB" if size > 1024 else f"{size}B"
                f.write(f"{rel_path} ({size_str})\n")
            except:
                f.write(f"{rel_path}\n")
        f.write("```\n\n")

        # Исходный код
        f.write("## 📄 Исходный код\n\n")

        code_extensions = {'.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh',
                          '.md', '.txt', '.sql', '.html', '.css'}
        special_files = {'.gitignore', '.env.example', 'Dockerfile', 'Makefile',
                        'requirements.txt', 'package.json'}

        for filepath, rel_path in sorted(all_files):
            ext = os.path.splitext(filepath)[1]
            filename = os.path.basename(filepath)

            # Проверяем, нужно ли включать файл
            if ext not in code_extensions and filename not in special_files:
                continue

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()

                # Определяем язык
                lang_map = {
                    '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                    '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
                    '.sh': 'bash', '.md': 'markdown', '.sql': 'sql',
                    '.html': 'html', '.css': 'css'
                }
                lang = lang_map.get(ext, 'text')

                f.write(f"### `{rel_path}`\n\n")
                f.write(f"```{lang}\n")
                f.write(content)
                f.write("\n```\n\n")
            except Exception as e:
                f.write(f"### `{rel_path}`\n\n[Ошибка чтения: {e}]\n\n")

    print(f"✅ Сохранено в: {output_file}")

if __name__ == "__main__":
    current_dir = Path.cwd()
    output_file = current_dir / "project_analysis.md"

    print(f"📁 Анализирую: {current_dir}")
    scan_directory(current_dir, output_file)
    print(f"📖 Готово! Открой: {output_file}")
```

### `requirements.txt`

```text
openpyxl>=3.1.5
requests>=2.32.3
pyyaml
vk-api
loguru>=0.7.3
```

### `setup.py`

```python
# use after git cloning.
import os
import getpass
from pathlib import Path

required_dirs = [
    'data',
    'data/xlsx',
    'data/docx'
]
required_files = [
    'users.yml',
    'ignored.txt'
]

def create():
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
        print(f"Создана папка: {directory}")
    for file in required_files:
        path = Path(file)
        if not path.exists():
            path.touch()
            print(f"Создан файл: {file}")

    if not (os.path.exists('token.txt') or os.getenv("BOT_TOKEN")):
        token=getpass.getpass("введи токен приложения VK:\n")
        with open ('token.txt', 'w') as f:
            f.write(token)
        print(f"токен успешно записан")


if __name__ == "__main__":
    create()
    print("установка успешно завершена!")
```

### `test_mail_helper.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.mail_helper import MailHelper

def test_mail_helper():
    """Test the updated mail helper functionality"""
    print("Testing MailHelper with club name and document name...")
    
    # Create a mock attachment file for testing
    test_file = "test_attachment.xlsx"
    with open(test_file, "w") as f:
        f.write("This is a test attachment file")
    
    try:
        mail_helper = MailHelper()
        # Test the updated send_mail method with club name and document name
        mail_helper.send_mail("ТестовыйКлуб", "ТестоваяСлужебка_2023_12_15", [test_file])
        print("SUCCESS: Mail sent with club name and document name in subject!")
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        # Clean up the test file
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_mail_helper()

```

### `test_mail_helper_simple.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Directly import only what we need
from utils.mail_helper import MailHelper

def test_mail_helper():
    """Test the updated mail helper functionality"""
    print("Testing MailHelper with club name and document name...")
    
    # Create a mock attachment file for testing
    test_file = "test_attachment.xlsx"
    with open(test_file, "w") as f:
        f.write("This is a test attachment file")
    
    try:
        mail_helper = MailHelper()
        # Test the updated send_mail method with club name and document name
        mail_helper.send_mail("ТестовыйКлуб", "ТестоваяСлужебка_2023_12_15", [test_file])
        print("SUCCESS: Mail sent with club name and document name in subject!")
    except Exception as e:
        print("ERROR: {}".format(e))
    finally:
        # Clean up the test file
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_mail_helper()

```

### `users.yml`

```yaml

```

### `utils/__init__.py`

```python
from .ignored_list import IgnoredList
from .excel_helper import *
from .vk_helper import *
from .net_helper import *



def get_secrets():
    # with open("token.txt", 'r') as f:
    #     token = f.readline()
    # with open("mail_password.txt", 'r') as f:
    #     mail_password = f.readline()
    token = os.getenv('BOT_TOKEN')
    mail_password = os.getenv('MAIL_PASSWORD')
    return {'token': token, 'mail_password': mail_password}

```

### `utils/excel_helper.py`

```python
import re
import openpyxl
from openpyxl.styles import PatternFill, Side, Border
from datetime import datetime, date 


def check_excel(path):
    rows = []
    data = openpyxl.load_workbook(path)
    sheet = data.active
    correct_meta = ['Корпус:', '№', 'Фамилия', 'Дата, время:', 'Имя', 'Отчество', 'Название мероприятия:',
                    'Серия и номер паспорта', 'Номер телефона', 'Ответственный от подразделения:',
                    'Калугина Анна Владимировна, ведущий менеджер ОМП', 79514373833, 'Контактное лицо:']
    meta = [sheet['A1'].value, sheet['A2'].value, sheet['B2'].value, sheet['C1'].value, sheet['C2'].value,
            sheet['D2'].value, sheet['E1'].value, sheet['E2'].value, sheet['F2'].value, sheet['G1'].value,
            sheet['G2'].value, sheet['G3'].value, sheet['H1'].value]
    korpus = sheet['B1'].value
    date_time = str(sheet['D1'].value)
    name = sheet['F1'].value
    rukovod = sheet['H2'].value
    rukovod_phone = sheet['H3'].value

    #correct_meta_otv = ['Романова Софья Александровна, директор ОМП', 79650431766]
    correct_meta_otv = ['Калугина Анна Владимировна, ведущий менеджер ОМП', 79514373833]

    date_str = date_time.split()[0]
    now = date.today()
    if correct_meta == meta:
        if date_time == "01.01.2025  09:00-23:00" or "Шаблон" in name or "Шаблон" in rukovod or rukovod_phone == 79633336075 or rukovod_phone == "79633336075":
            return "01", rows
        date_time = datetime.strptime(str(date_time.split()[0]), "%d.%m.%Y").date()
        if date_time < now:
            return "02", rows
        i = 0
        j = 0
        cyrillic_lower_letters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя- '
        while True:
            j += 1
            col = str(j)
            if sheet['A' + col].value is None: break
        lenrow = j - 3
        while True:
            i += 1
            col = str(i)
            if sheet['A' + col].value is None: break
            row = [sheet['A' + col].value, sheet['B' + col].value.strip(), sheet['C' + col].value.strip(),
                   str(sheet['D' + col].value).strip(), (str(sheet['E' + col].value).replace(" ", "").zfill(10) if i>3 else str(sheet['E' + col].value)),
                   str(sheet['F' + col].value).strip(), sheet['G' + col].value, sheet['H' + col].value]

            if i < 3:
                if i == 2: row[6] = correct_meta_otv[0]
                rows.append(row)
                continue

            if i == 3:

                digits = re.findall(r"7\d{10}", str(int(float(row[6]))))[0]
                row[6] = correct_meta_otv[1]
                digits = re.findall(r"7\d{10}", str(int(float(row[7]))))[0]
                row[7] = digits


            if row[0] != i - 2: return "A" + col
            for _ in row[1].lower():
                if _ not in cyrillic_lower_letters: return "B" + col
            row[1] = row[1][0].upper() + row[1][1:].lower()
            for _ in row[2].lower():
                if _ not in cyrillic_lower_letters: return "C" + col + _
            row[2] = row[2][0].upper() + row[2][1:].lower()
            if str(row[3]) != "None":
                for _ in str(row[3]).lower():
                    if _ not in cyrillic_lower_letters:
                        return "D" + col
                row[3] = row[3][0].upper() + row[3][1:].lower()
            else:
                row[3] = ""

            if not ((row[4].isdigit() or row[4].replace(".", "", 1).isdigit()) or not (
            re.findall(r"\d{10}", row[4]))) or row[4][:2] == '00': return "E" + col
            digits = re.findall(r"\d{10}", str(int(float(row[4]))).zfill(10))[0]
            row[4] = digits
            if not (row[5].isdigit() or row[5].replace(".", "", 1).isdigit()) or not (
            re.findall(r"7\d{10}", row[5])): return "F" + col
            digits = re.findall(r"7\d{10}", str(int(float(row[5]))))[0]
            if not digits: return "F" + col
            if lenrow > 2:
                nomer = "8-" + digits[1:4] + "-" + digits[4:7] + "-" + digits[7:9] + "-" + digits[9:]  # 8-xxx-xxx-xx-xx
            else:
                nomer = digits
            row[5] = nomer
            rows.append(row)
    else:
        return "00", rows
    return "success", rows


def create_excel(path, rows):
    data = openpyxl.Workbook()
    sheet = data.active

    sheet.title = "Согласование СЗ"
    fill = PatternFill(start_color="E7E6E6", end_color="E7E6E6", fill_type="solid")
    border = Border(
        left=Side(border_style="medium", color='FF000000'),
        right=Side(border_style="medium", color='FF000000'),
        top=Side(border_style="medium", color='FF000000'),
        bottom=Side(border_style="medium", color='FF000000'),
        diagonal=Side(border_style="medium", color='FF000000'),
        diagonal_direction=0,
        outline=Side(border_style="medium", color='FF000000'),
        vertical=Side(border_style="medium", color='FF000000'),
        horizontal=Side(border_style="medium", color='FF000000')
    )

    for i in range(len(rows)):
        for j in range(len(rows[i])):
            cell = sheet.cell(row=i + 1, column=j + 1)
            cell.value = rows[i][j]
            if cell.value:
                cell.border = border

    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column_letter].width = adjusted_width

    sheet["A1"].fill = fill
    sheet["C1"].fill = fill
    sheet["E1"].fill = fill
    sheet["G1"].fill = fill
    sheet["H1"].fill = fill
    sheet["A2"].fill = fill
    sheet["B2"].fill = fill
    sheet["C2"].fill = fill
    sheet["D2"].fill = fill
    sheet["E2"].fill = fill
    sheet["F2"].fill = fill
    sheet["G2"].fill = fill
    sheet["G3"].fill = fill
    try:
        data.save(path)
        return True
    except:
        print("ERROR")
        return False

```

### `utils/ignored_list.py`

```python
# -*- coding: utf-8 -*-

class IgnoredList:
    def __init__(self):
        self.ignored = set()

    def add(self, uid):
        if uid not in self.ignored:
            self.ignored.add(uid)
            print("Пользователь {} добавлен в игнор.".format(uid))
        else:
            print("Пользователь {} уже в игноре.".format(uid))

    def remove(self, uid):
        if uid in self.ignored:
            self.ignored.remove(uid)
            print("Пользователь {} удалён из игнора.".format(uid))
        else:
            print("Пользователь {} не найден в списке игнорируемых.".format(uid))

    def is_ignored(self, uid):
        return uid in self.ignored

    def clear(self):
        self.ignored.clear()
        print("Список игнорируемых пользователей очищен.")

    def save_to_file(self):
        try:
            with open("data/ignored.txt", 'w+') as file:
                file.write('\n'.join(map(str, self.ignored)))
            print("Список игнорируемых сохранён.")
        except Exception as e:
            print("Ошибка при сохранении: {}".format(e))

    def load_from_file(self):
        try:
            with open("data/ignored.txt", 'r') as file:
                self.ignored = set(map(lambda x: int(x.strip()), file.readlines()))
            return ("Список игнорируемых загружен.")
        except Exception as e:
            print("Ошибка при загрузке: {}".format(e))

```

### `utils/log.py`

```python
import logging

logger = logging.getLogger()

formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%d.%m.%y %H:%M:%S")

file_handler = logging.FileHandler("data/py.log", mode="a")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log():
    def info(_):
        logger.info(_)
    def warn(_):
        logger.warning(_)
    def error(_):
        logger.error(_)

    return info, error

```

### `utils/mail_helper.py`

```python
import imaplib
import os
import smtplib
import time

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

from utils import get_secrets

class MailHelper:
    def __init__(self):
        self.our_addr = 'omp@itmo.ru'
        self.ufb_addr = 'dberman@itmo.ru'
        self.body = """
        
        <p>ЭТО ТЕСТ НОВОЙ ФИЧИ. ИГНОРИРУЙТЕ! Здравствуйте! Прошу согласовать служебную записку во вложении.</p>
        <br>
        
        <blockquote>
        <img src="https://itmo.ru/file/pages/213/logo_osnovnoy_russkiy_chernyy.png" alt="ITMO" width="150"><br>
        <p>С уважением, Берман Денис Константинович<br> 
        Офис молодежных проектов | Youth Projects Office<br>
        <em>Кронверкский пр., 49, лит. А, оф. 1111, Санкт-Петербург, Россия | Kronverksky Pr. 49, bldg. A, off. 1111, St. Petersburg, Russia<br>
        Email: omp@itmo.ru<br></em>
        <strong>Университет ИТМО | ITMO University <strong><br>
        <a href="https://itmo.ru/">itmo.ru</a>
        </p>
        </blockquote>
        """
        self.mail_password = get_secrets()["mail_password"]

    def send_mail(self, club_name, document_name, attachments):
        msg = MIMEMultipart()
        #Формируем сообщение
        msg['Subject'] = f"Согласование СЗ: {club_name} - {document_name}"
        msg['From'] = self.our_addr; msg['To'] = self.ufb_addr
        
        # Создаем более информативное тело письма
        informative_body = f"""
        <p>Здравствуйте!</p>
        <p>Прошу согласовать служебную записку во вложении.</p>
        <p><strong>Клуб:</strong> {club_name}</p>
        <p><strong>Документ:</strong> {document_name}</p>
        <p><strong>Идентификатор:</strong> AUTO-{int(time.time())}</p>
        <br>
        
        <blockquote>
        <img src="https://itmo.ru/file/pages/213/logo_osnovnoy_russkiy_chernyy.png" alt="ITMO" width="150"><br>
        <p>С уважением, Берман Денис Константинович<br> 
        Офис молодежных проектов | Youth Projects Office<br>
        <em>Кронверкский пр., 49, лит. А, оф. 1111, Санкт-Петербург, Россия | Kronverksky Pr. 49, bldg. A, off. 1111, St. Petersburg, Russia<br>
        Email: omp@itmo.ru<br></em>
        <strong>Университет ИТМО | ITMO University <strong><br>
        <a href="https://itmo.ru/">itmo.ru</a>
        </p>
        </blockquote>
        """
        
        msg.attach(MIMEText(informative_body, 'html'))

        for attachment in attachments:
            if not os.path.isfile(attachment):
                print(attachment)
                continue
            with open(attachment, 'rb') as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment)}"'
                msg.attach(part)

        #Логинимся и отправляем
        with smtplib.SMTP_SSL('smtp.mail.ru', 465) as mail:
            mail.login('omp@itmo.ru', self.mail_password)
            mail.sendmail(self.our_addr, self.ufb_addr, msg.as_string())
        self.save_mail(msg)

    def save_mail(self, msg):
        with imaplib.IMAP4_SSL('imap.mail.ru') as imap:
            imap.login(self.our_addr, self.mail_password)

            #Отправка в нужную папку
            sent_folder = '&BCMEJAQR-'
            imap.select(sent_folder)
            imap.append(sent_folder, '', imaplib.Time2Internaldate(time.time()), msg.as_bytes())

            #Сразу помечаем прочитанным
            status, data = imap.search(None, 'HEADER', 'Message-ID', msg['Message-ID'])
            email_ids = data[0].split()
            for email_id in email_ids:
                imap.store(email_id, '+FLAGS', '\\Seen')

            imap.logout()

```

### `utils/mail_integration_helpers.py`

```python
import json
from datetime import datetime
from .mail_sync_worker import MailSyncManager


def save_sent_document(doc_id, filename, sender_uid, org):
    try:
        manager = MailSyncManager()
        if not manager.worker:
            return False

        sent_docs = manager.worker.mail_receiver.load_sent_docs()

        sent_docs[doc_id] = {
            'id': doc_id,
            'filename': filename,
            'sender_uid': sender_uid,
            'org': org,
            'sent_at': datetime.now().isoformat(),
            'status': 'sent'
        }

        with open('data/sent_docs.json', 'w', encoding='utf-8') as f:
            json.dump(sent_docs, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f'Error saving sent document: {e}')
        return False


def handle_admin_commands(msg, uid, admins):
    msg_lower = msg.lower()

    if msg_lower == '!sync' and uid in admins:
        manager = MailSyncManager()
        result = manager.force_sync()

        if result['status'] == 'success':
            return (uid, 'Mail sync completed')
        else:
            return (uid, f"Sync error: {result['message']}")

    if msg_lower == '!mail_stats' and uid in admins:
        manager = MailSyncManager()
        metrics = manager.get_metrics()

        message = (
            f"Sent documents: {metrics.get('sent_documents', 0)}\n"
            f"Received emails: {metrics.get('received_emails', 0)}\n"
            f"Last check: {metrics.get('last_check', 'Never')}"
        )
        return (uid, message)

    if msg_lower == '!mail_report' and uid in admins:
        try:
            with open('data/reconciliation_report.json', 'r', encoding='utf-8') as f:
                report = json.load(f)

            count = report.get('reconciled_count', 0)
            message = f'Reconciled documents: {count}'
            return (uid, message)
        except:
            return (uid, 'No reconciliation report found')

    return None

```

### `utils/mail_poller.py`

```python
import logging
import threading
import time
from typing import Optional

log = logging.getLogger(__name__)

class MailPoller:
    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        protocol: str = "IMAP",
        poll_interval_sec: int = 15,
    ):
        self.host = host
        self.user = user
        self.password = password
        self.protocol = protocol.upper()
        self.poll_interval_sec = max(5, int(poll_interval_sec))

    def _poll_once(self) -> None:
        """
        Заглушка для будущей реализации.
        Тут будеn:
          - IMAP IDLE или
          - раз в N сек делаться SEARCH/UID SEARCH и обрабатываться новые письма
        Сейчас просто имитация.
        """
        log.debug("MailPoller: tick (host=%s, user=%s)", self.host, self.user)
        # TODO: заменить на реальную работу с почтой
        time.sleep(0.1)

    def run(self, stop_event: threading.Event) -> None:
        log.info("MailPoller: starting (interval=%ss)", self.poll_interval_sec)
        while not stop_event.is_set():
            try:
                self._poll_once()
            except Exception as e:
                log.exception("MailPoller error: %s", e)
                if stop_event.wait(3.0):
                    break
            if stop_event.wait(self.poll_interval_sec):
                break
        log.info("MailPoller: stopped")
```

### `utils/mail_reciever.py`

```python
import imaplib
import json
import logging
from email.header import decode_header
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import hashlib
from pathlib import Path

from utils import get_secrets

logger = logging.getLogger(__name__)





class MailReceiver:

    def __init__(self):
        self.our_addr = 'omp@itmo.ru'
        self.ufb_addr = 'dberman@itmo.ru'
        self.imap_server = 'imap.mail.ru'
        self.imap_port = 993
        self.imap = None

        secrets = get_secrets()
        self.mail_password = secrets.get('mail_password')

        self.sent_docs_file = 'data/sent_docs.json'
        self.received_docs_file = 'data/received_docs.json'
        self._init_storage()

    def _decode_mime_header(self, value) -> str:
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')

        if isinstance(value, str):
            try:
                decoded_parts = decode_header(value)
                result = ""
                for part, encoding in decoded_parts:
                    if isinstance(part, bytes):
                        if encoding:
                            result += part.decode(encoding, errors='ignore')
                        else:
                            result += part.decode('utf-8', errors='ignore')
                    else:
                        result += str(part).strip()
                return result.strip()
            except:
                return value

        return str(value)
    def _init_storage(self):
        Path('data').mkdir(exist_ok=True)

        for filepath in [self.sent_docs_file, self.received_docs_file]:
            if not Path(filepath).exists():
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)

    def connect(self) -> bool:
        try:
            self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.imap.login(self.our_addr, self.mail_password)
            logger.info(f'Connected to IMAP: {self.imap_server}')
            return True
        except Exception as e:
            logger.error(f'Failed to connect IMAP: {e}')
            return False

    def disconnect(self):
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass

    def _decode_header(self, value) -> str:
        if isinstance(value, bytes):
            return value.decode('utf-8', errors='ignore')

        if isinstance(value, str):
            return value

        try:
            decoded_parts = decode_header(value)
            result = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    result += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    result += str(part)
            return result
        except:
            return str(value)

    def fetch_emails(self, days: int = 7) -> List[Dict]:
        if not self.imap:
            logger.error('IMAP not connected')
            return []

        try:
            ufb_folder = '&BCMEJAQR-'
            self.imap.select(ufb_folder)

            since_date = (datetime.now() - timedelta(days=days)).strftime('%d-%b-%Y')
            status, email_ids = self.imap.search(None, f'SINCE {since_date}')

            if status != 'OK':
                logger.warning(f'Email search failed: {status}')
                return []

            emails = []
            for email_id in email_ids[0].split():
                status, msg_data = self.imap.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    continue

                try:
                    import email
                    msg = email.message_from_bytes(msg_data[0][1])
                    email_info = self._parse_email(msg, email_id)
                    if email_info:
                        emails.append(email_info)
                except Exception as e:
                    logger.warning(f'Error parsing email: {e}')

            logger.info(f'Fetched {len(emails)} emails from UFB folder')
            return emails

        except Exception as e:
            logger.error(f'Error fetching emails: {e}')
            return []

    def _parse_email(self, msg, email_id: bytes) -> Optional[Dict]:
        try:
            subject = self._decode_mime_header(msg.get('Subject', ''))
            sender = self._decode_mime_header(msg.get('From', ''))
            date_str = msg.get('Date', datetime.now().isoformat())

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
            else:
                try:
                    body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                except:
                    body = msg.get_payload()

            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_disposition() == 'attachment':
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                'filename': self._decode_header(filename),
                                'content_type': part.get_content_type(),
                                'size': len(part.get_payload(decode=True))
                            })

            email_hash = hashlib.md5(
                f'{subject}|{sender}|{date_str}'.encode()
            ).hexdigest()[:16]

            return {
                'id': email_hash,
                'email_id': email_id.decode(),
                'subject': subject,
                'sender': sender,
                'date': date_str,
                'body': body[:500],
                'attachments': attachments,
                'received_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f'Error parsing email: {e}')
            return None

    def save_received_email(self, email_info: Dict):
        try:
            with open(self.received_docs_file, 'r', encoding='utf-8') as f:
                docs = json.load(f)

            docs[email_info['id']] = email_info

            with open(self.received_docs_file, 'w', encoding='utf-8') as f:
                json.dump(docs, f, ensure_ascii=False, indent=2)

            logger.info(f'Saved email: {email_info["subject"]}')

        except Exception as e:
            logger.error(f'Error saving email: {e}')

    def load_sent_docs(self) -> Dict:
        try:
            with open(self.sent_docs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f'Error loading sent_docs: {e}')
            return {}

    def load_received_docs(self) -> Dict:
        try:
            with open(self.received_docs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f'Error loading received_docs: {e}')
            return {}

    def compare_documents(self, sent_doc: Dict, received_doc: Dict) -> Dict:
        matches = {
            'subject_match': False,
            'sender_match': False,
            'date_match': False,
            'status': 'NOT_MATCHED',
            'confidence': 0
        }

        sent_filename = sent_doc.get('filename', '').lower()
        received_subject = received_doc.get('subject', '').lower()

        # Improved subject matching for auto-approval emails
        if 'согласование сз:' in received_subject and 're:' in received_subject:
            matches['subject_match'] = True

        received_sender = received_doc.get('sender', '').lower()

        if 'pass@itmo.ru' in received_sender or 'dberman@itmo.ru' in received_sender:
            matches['sender_match'] = True

        try:
            sent_date = datetime.fromisoformat(sent_doc.get('sent_at', ''))
            received_date = datetime.fromisoformat(received_doc.get('date', ''))

            if received_date > sent_date and (received_date - sent_date).total_seconds() < 86400 * 7:
                matches['date_match'] = True
        except:
            pass

        confidence = sum([
            matches['subject_match'] * 50,  # Increased weight for better matching
            matches['sender_match'] * 30,
            matches['date_match'] * 20
        ])
        matches['confidence'] = confidence

        if confidence >= 80:  # Increased threshold for better accuracy
            matches['status'] = 'LIKELY_MATCH'
        elif confidence >= 60:
            matches['status'] = 'POSSIBLE_MATCH'
        else:
            matches['status'] = 'NOT_MATCHED'

        return matches

    def auto_reconcile(self, min_confidence: int = 70) -> List[Dict]:
        sent_docs = self.load_sent_docs()
        received_docs = self.load_received_docs()
        reconciled = []

        logger.info(f'Comparing {len(sent_docs)} sent vs {len(received_docs)} received')

        for sent_id, sent_doc in sent_docs.items():
            best_match = None
            best_confidence = 0

            for received_id, received_doc in received_docs.items():
                comparison = self.compare_documents(sent_doc, received_doc)

                if comparison['confidence'] > best_confidence:
                    best_confidence = comparison['confidence']
                    best_match = {
                        'sent_doc_id': sent_id,
                        'received_doc_id': received_id,
                        'comparison': comparison
                    }

            if best_match and best_confidence >= min_confidence:
                best_match['status'] = 'RECONCILED'
                reconciled.append(best_match)

                logger.info(
                    f'Reconciled: {sent_doc["filename"]} '
                    f'(confidence: {best_confidence}%)'
                )

        logger.info(f'Total reconciled: {len(reconciled)}')
        return reconciled

    def export_reconciliation_report(self, reconciled: List[Dict],
                                     output_file: str = 'data/reconciliation_report.json'):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'generated_at': datetime.now().isoformat(),
                    'reconciled_count': len(reconciled),
                    'reconciled_docs': reconciled
                }, f, ensure_ascii=False, indent=2)

            logger.info(f'Report saved: {output_file}')
        except Exception as e:
            logger.error(f'Error saving report: {e}')

```

### `utils/mail_sync_worker.py`

```python
import threading
import time
import logging
from datetime import datetime
from typing import Optional

from utils.mail_reciever import MailReceiver

logger = logging.getLogger(__name__)


class MailSyncWorker:

    def __init__(self, poll_interval: int = 300, min_confidence: int = 80):
        self.poll_interval = poll_interval
        self.min_confidence = min_confidence

        self.mail_receiver = MailReceiver()
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            logger.warning('Worker already running')
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info(f'MailSyncWorker started (interval: {self.poll_interval}s)')

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.mail_receiver.disconnect()
        logger.info('MailSyncWorker stopped')

    def _run_loop(self):
        while self.running:
            try:
                self._sync_once()
            except Exception as e:
                logger.error(f'Error in MailSyncWorker: {e}')

            for _ in range(self.poll_interval):
                if not self.running:
                    break
                time.sleep(1)

    def _sync_once(self):
        logger.debug(f'Starting sync at {datetime.now().isoformat()}')

        if not self.mail_receiver.connect():
            logger.error('Failed to connect IMAP')
            return

        try:
            emails = self.mail_receiver.fetch_emails(days=7)

            for email_info in emails:
                self.mail_receiver.save_received_email(email_info)

            reconciled = self.mail_receiver.auto_reconcile(
                min_confidence=self.min_confidence
            )

            self.mail_receiver.export_reconciliation_report(reconciled)

            logger.info(f'Sync completed: {len(reconciled)} reconciled')

        finally:
            self.mail_receiver.disconnect()


class MailSyncManager:
    _instance: Optional['MailSyncManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.worker = None
        return cls._instance

    def start(self, poll_interval: int = 300):
        if self.worker is not None and self.worker.running:
            logger.warning('MailSyncManager already running')
            return

        self.worker = MailSyncWorker(poll_interval)
        self.worker.start()

    def stop(self):
        if self.worker:
            self.worker.stop()

    def force_sync(self) -> dict:
        if not self.worker:
            return {'status': 'error', 'message': 'Worker not initialized'}

        try:
            self.worker._sync_once()
            return {'status': 'success', 'message': 'Sync completed'}
        except Exception as e:
            logger.error(f'Error during force sync: {e}')
            return {'status': 'error', 'message': str(e)}

    def get_metrics(self) -> dict:
        if not self.worker:
            return {}

        try:
            sent = self.worker.mail_receiver.load_sent_docs()
            received = self.worker.mail_receiver.load_received_docs()

            return {
                'sent_documents': len(sent),
                'received_emails': len(received),
                'last_check': datetime.now().isoformat()
            }
        except:
            return {}


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    manager = MailSyncManager()
    manager.start(poll_interval=60)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Stopping...')
        manager.stop()

```

### `utils/metrics.py`

```python
import os
import yaml
from datetime import datetime

class Metrics:
    def __init__(self):
        self.data = {
            "memo_received": 0,
            "memo_approved": 0,
            "memo_filtered": 0,
            "message": 0,
            "errors": 0,
            "manager": 0,
            "history": []
        }
        self.filename = "data/metrics.yaml"
        if os.path.exists(self.filename):
            self.load_from_file()

    def record_memo_received(self, trigger):
        self.data["memo_received"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_received",
            "trigger": trigger
        })
        self.save_to_file()

    def record_memo_approved(self, trigger):
        self.data["memo_approved"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_approved",
            "trigger": trigger
        })
        self.save_to_file()

    def record_memo_filtered(self, trigger):
        self.data["memo_filtered"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "memo_filtered",
            "trigger": trigger
        })
        self.save_to_file()

    def record_message(self, trigger):
        self.data["message"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "message",
            "trigger": trigger
        })
        self.save_to_file()

    def record_error(self, trigger):
        self.data["errors"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "error",
            "trigger": trigger
        })
        self.save_to_file()

    def record_manager(self, trigger):
        self.data["manager"] += 1
        self.data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "manager",
            "trigger": trigger
        })
        self.save_to_file()

    def save_to_file(self):
        try:
            data_ordered = {
                "memo_received": self.data.get("memo_received", 0),
                "memo_approved": self.data.get("memo_approved", 0),
                "memo_filtered": self.data.get("memo_filtered", 0),
                "message": self.data.get("message", 0),
                "manager": self.data.get("manager", 0),
                "errors": self.data.get("errors", 0),
                "history": self.data.get("history", [])
            }
            with open(self.filename, "w", encoding="utf-8") as file:
                yaml.dump(data_ordered, file, allow_unicode=True)
        except Exception as e:
            print(f"Ошибка при сохранении метрик: {e}")

    def load_from_file(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file)
                if loaded is not None:
                    self.data = loaded
                else:
                    self.data = {
                        "memo_received": 0,
                        "memo_approved": 0,
                        "memo_filtered": 0,
                        "message": 0,
                        "errors": 0,
                        "manager": 0,
                        "history": []
                    }
                    self.save_to_file()
        except Exception as e:
            print(f"Ошибка при загрузке метрик: {e}")

    def get_report(self):
        report = (
            f"Всего сообщений: {self.data.get('message', 0)}\n"
            f"Ошибок при обработке: {self.data.get('errors', 0)}\n"
            f"Помощь менеджера понадобилась: {self.data.get('manager', 0)}\n"
            "\n"
            f"Поступило служебок: {self.data.get('memo_received', 0)}\n"
            f"Одобрено служебок: {self.data.get('memo_approved', 0)}\n"
            f"Отфильтровано служебок: {self.data.get('memo_filtered', 0)}\n"
        )
        return report
```

### `utils/net_helper.py`

```python
# IP file - connections, requests, responses, etc.
import requests
import os
from datetime import datetime as date
from utils.log import *


def attachment_extract(url, name, ext):
    response = requests.get(url)

    if not os.path.exists('data/' + ext + '/' + name):
        dir = 'data/' + ext +"/" + name
        os.mkdir(dir)
    path = 'data/' + ext + "/" + name + "/" + ("_".join(str(date.now())[:-7].replace(":", "-").split())) + "." + ext
    with open(path, "wb") as f:
        f.write(response.content)
        return path

```

### `utils/user_list.py`

```python
import yaml

class UserList:
    def __init__(self):
        self.users = {}  # Формат: {uid: set(clubs)}
        self.clubs = set()

    def add(self, uid, club):
        self.load_from_file()

        if uid not in self.users:
            self.users[uid] = set()
        if club not in self.users[uid]:
            self.users[uid].add(club)
            self.clubs.add(club)
            print(f"Пользователь {uid} теперь руководит клубом {club}.")
        else:
            print(f"Пользователь {uid} уже руководит клубом {club}.")

        self.save_to_file()

    # def remove(self, uid, club=None):
    #     if uid not in self.users:
    #         print(f"Пользователь {uid} не найден в списке.")
    #         return
    #
    #     if club:
    #         if club in self.users[uid]:
    #             self.users[uid].remove(club)
    #             print(f"Клуб {club} удалён у пользователя {uid}.")
    #             if not self.users[uid]:  # Если у пользователя больше нет клубов, удаляем его
    #                 del self.users[uid]
    #                 print(f"Пользователь {uid} удалён из списка, так как больше не руководит ни одним клубом.")
    #         else:
    #             print(f"Пользователь {uid} не руководит клубом {club}.")
    #     else:
    #         del self.users[uid]
    #         print(f"Пользователь {uid} полностью удалён из списка.")

    def is_user(self, uid):
        return uid in self.users

    def get_clubs(self, uid):
        return self.users.get(uid, set())

    # def clear(self):
    #     self.users.clear()
    #     self.clubs.clear()
    #     print("Список пользователей и клубов очищен.")

    def save_to_file(self, filename="data/users.yml"):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                yaml.dump({str(uid): list(clubs) for uid, clubs in self.users.items()}, file, allow_unicode=True)
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")

    def load_from_file(self, filename="users.yml"):
        try:
            with open(filename, "r+", encoding="utf-8") as file:
                data = yaml.safe_load(file)
                if data is not None:
                    self.users = {int(uid): set(clubs) for uid, clubs in data.items()}
                    self.clubs = {club for clubs in self.users.values() for club in clubs}
                else:
                    self.users = {}
                    self.clubs = set()
        except Exception as e:
            print(f"Ошибка при загрузке: {e}")

```

### `utils/vk_helper.py`

```python
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import vk_api


class VKHelper:
    def __init__(self, vk_session):
        self.vk = vk_session.get_api()
        self.vk_session = vk_session

    def lsend(self, id, text):
        print("sended to " + str(id))
        self.vk_session.method('messages.send', {'user_id': id, 'message': text, 'random_id': 0})

    def lsend_withA(self, id, text, attachment):
        print("sended to " + str(id))
        self.vk_session.method('messages.send',
                               {'user_id': id, 'message': text, 'attachment': attachment, 'random_id': 0})

    def send(self, id, text):
        print("sended to " + str(id))
        self.vk_session.method('messages.send', {'chat_id': id, 'message': text, 'random_id': 0})

    def send_withA(self, id, text, attachment, title, sender):
        print("sended to " + str(id))
        keyboard = vk_api.keyboard.VkKeyboard(inline=True)
        keyboard.add_callback_button(label="ОТПРАВИТЬ", payload={"type": "send", 'sender': sender, 'title': title},
                                     color=VkKeyboardColor.SECONDARY)
        keyboard.add_callback_button(label="СОГЛАСОВАТЬ",
                                     payload={"type": "approve", 'sender': sender, 'title': title, 'isSended': False},
                                     color=VkKeyboardColor.POSITIVE)

        keyboard = keyboard.get_keyboard()
        self.vk_session.method('messages.send',
                               {'chat_id': id, 'message': text, 'attachment': attachment, 'keyboard': keyboard,
                                'random_id': 0})

    def sender(self, sender_type):
        pass

    def editkb(self, peer_id, cmid, type, sender, title):
        keyboard = vk_api.keyboard.VkKeyboard(inline=True)
        keyboard.add_callback_button(label="ОТПРАВЛЕНО", payload={"type": "sended", 'sender': sender, 'title': title},
                                     color=VkKeyboardColor.NEGATIVE)
        keyboard.add_callback_button(label=("СОГЛАСОВАНО" if type == "approve" else "СОГЛАСОВАТЬ"),
                                     payload={"type": ("approved" if type == "approve" else "approve"),
                                              'sender': sender,
                                              'title': title, 'isSended': (False if type == "send" else True)},
                                     color=(
                                         VkKeyboardColor.NEGATIVE if type == "approved" else VkKeyboardColor.POSITIVE))
        keyboard = keyboard.get_keyboard()

        original_message = self.vk.messages.getById(
            peer_id=peer_id,
            cmids=cmid)
        original_text = original_message['items'][0]['text']
        original_attachment = original_message['items'][0]['attachments'][0]['doc']
        original_attachment = "doc" + str(original_attachment['owner_id']) + '_' + str(original_attachment['id'])

        self.vk.messages.edit(peer_id=peer_id, conversation_message_id=cmid, keyboard=keyboard, message=original_text,
                              attachment=original_attachment)

    def send_message(self, peer_id, message, keyboard=None, attachment=None):
        payload = {
            "peer_id": peer_id,
            "message": message,
            "random_id": 0
        }
        if keyboard:
            payload["keyboard"] = keyboard
        if attachment:
            payload["attachment"] = attachment

        try:
            self.vk.messages.send(**payload)
        except vk_api.exceptions.ApiError as e:
            raise Exception(f"Ошибка отправки сообщения: {e}")

    def edit_keyboard(self, peer_id, cmid, keyboard):
        try:
            original_message = self.vk.messages.getById(
                peer_id=peer_id,
                cmids=cmid)
            original_text = original_message['items'][0]['text']
            attachments = original_message['items'][0].get('attachments', [])
            if attachments:
                doc = attachments[0].get('doc')
                if doc:
                    original_attachment = "doc" + str(doc['owner_id']) + '_' + str(doc['id'])
                else:
                    original_attachment = None
            else:
                original_attachment = None
            if keyboard is None:
                self.vk.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=cmid,
                    message=original_text,
                    attachment=original_attachment
                )
            else:
                self.vk.messages.edit(
                    peer_id=peer_id,
                    conversation_message_id=cmid,
                    keyboard=keyboard,
                    message=original_text,
                    attachment=original_attachment
                )
        except vk_api.exceptions.ApiError as e:
            raise Exception(f"Ошибка изменения клавиатуры: {e}")

    def create_keyboard(self, buttons):
        keyboard = VkKeyboard(inline=True)
        for button in buttons:
            if button.get("newline"): keyboard.add_line()
            keyboard.add_callback_button(
                label=button["label"],
                payload=button["payload"],
                color=getattr(VkKeyboardColor, button["color"].upper())
            )
        return keyboard.get_keyboard() if buttons else None

    def create_standart_keyboard(self, buttons):
        keyboard = VkKeyboard(inline=False)
        for button in buttons:
            if button.get("newline"): keyboard.add_line()
            keyboard.add_button(
                label=button["label"],
                payload=button["payload"],
                color=getattr(VkKeyboardColor, button["color"].upper())
            )

        return keyboard.get_keyboard()

    def create_link_keyboard(self, buttons):
        keyboard = VkKeyboard(inline=True)
        for button in buttons:
            if button.get("newline"): keyboard.add_line()
            keyboard.add_openlink_button(
                label=button["label"],
                payload=button["payload"],
                link=button["link"]
            )

        return keyboard.get_keyboard()

```

