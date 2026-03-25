# Cloud-based Knowledge Card System (Django)

This repository is a Django-based knowledge card system designed for CIS 4517 project requirements, including AWS EC2 deployment and S3 image storage.

## Prerequisites

- AWS account with permissions to manage EC2, S3, IAM
- AWS CLI installed and configured locally (`aws configure`)
- An EC2 key pair for SSH
- Python 3.11+ (project uses 3.12 in venv in this repo)
- Git installed

## Local setup (recommended before EC2 deployment)

1. Clone the repository:

```bash
git clone <repo_url>
cd Cloud-based_Knowledge_Card_System
```

2. Create and activate virtual environment:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows cmd
.\.venv\Scripts\activate.bat
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file in project root with environment configuration:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
USE_S3=0
# for S3 mode:
# AWS_ACCESS_KEY_ID=your-access-key-id
# AWS_SECRET_ACCESS_KEY=your-secret-access-key
# AWS_STORAGE_BUCKET_NAME=your-bucket-name
# AWS_S3_REGION_NAME=us-east-1
```

5. Apply migrations and seed data:

```bash
python manage.py migrate
python manage.py seed_cards
```

6. Run locally:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000`.

## AWS setup

### 1. S3 bucket (image storage)

- Create bucket in AWS S3 console.
- Enable public access for development or configure bucket policies for private access.
- (Optional) enable versioning and lifecycle rules.

### 2. IAM role and policy

1. Create IAM policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

2. Create IAM role for EC2 and attach the policy.
3. You may also create an IAM user for local testing and configure `aws configure` with its access key.

### 3. EC2 instance launch

1. In AWS console, launch EC2 (Amazon Linux 2023 or Ubuntu 22.04).
2. Assign the IAM role created above.
3. Choose instance type (e.g., t3.micro for free tier).
4. Set Security Group rules:
   - SSH (TCP 22) from your IP
   - HTTP (TCP 80) from anywhere (or your IP)
   - Custom TCP 8000 from necessary IPs (if using runserver)
5. Add your SSH key pair.

### 4. SSH to EC2

```bash
ssh -i /path/to/your-key.pem ec2-user@<ec2-public-ip>
# or ubuntu@<ip> for Ubuntu AMIs
```

### 5. Install dependencies on EC2

```bash
sudo yum update -y          # or sudo apt update && sudo apt upgrade
sudo yum install -y git python3 python3-venv gcc openssl-devel libjpeg-turbo-devel
# Ubuntu
# sudo apt-get install -y git python3 python3-venv python3-pip build-essential libpq-dev

git clone <repo_url>
cd Cloud-based_Knowledge_Card_System
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 6. Configure `.env` on EC2

```bash
cat > .env << 'EOF'
DJANGO_SECRET_KEY=some-super-secret
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=<ec2-public-ip>,localhost
USE_S3=1
AWS_ACCESS_KEY_ID=<access_key>
AWS_SECRET_ACCESS_KEY=<secret_key>
AWS_STORAGE_BUCKET_NAME=<bucket-name>
AWS_S3_REGION_NAME=<region>
EOF
```

### 7. Database + migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_cards  # optional
```

### 8. Run app on EC2

For simple testing:

```bash
python manage.py runserver 0.0.0.0:8000
```

For production, use Gunicorn + nginx (recommended):

```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 knowledge_card_system.wsgi
```

Then configure nginx to proxy pass to `http://127.0.0.1:8000`.

## Notes

- AWS permission requirement: EC2 instance role must allow S3 access to your bucket.
- Ensure `USE_S3=1` for uploads to go to AWS S3; otherwise the app uses local `MEDIA_ROOT`.
- Add `DJANGO_ALLOWED_HOSTS` to include your EC2 host.

## Quick command recap

```bash
# on EC2
cd Cloud-based_Knowledge_Card_System
source .venv/bin/activate
python manage.py migrate
python manage.py seed_cards
python manage.py runserver 0.0.0.0:8000
```

This now reflects current app behavior and required AWS EC2/S3 deployment workflow.
