"""Run inside the deployed container with its DATA_DIR mounted. No public admin endpoint."""
import argparse,time
from app import db,init_db
parser=argparse.ArgumentParser(description='THREAD account administration')
sub=parser.add_subparsers(dest='command',required=True)
a=sub.add_parser('approve-seller');a.add_argument('email')
a=sub.add_parser('revoke-seller');a.add_argument('email')
a=sub.add_parser('grant-paid');a.add_argument('email');a.add_argument('--days',type=int,default=30)
a=sub.add_parser('reset-download');a.add_argument('job_id')
args=parser.parse_args();init_db(recover=False)
with db() as c:
    if args.command=='reset-download':
        changed=c.execute('UPDATE jobs SET downloads=0 WHERE id=?',(args.job_id,)).rowcount
        if not changed:raise SystemExit('Job not found')
    else:
        user=c.execute('SELECT id,role FROM users WHERE email=?',(args.email.strip().lower(),)).fetchone()
        if not user:raise SystemExit('User not found. Sign up first.')
        if user['role']!='seller':raise SystemExit('This account is not a seller.')
        if args.command in ('approve-seller','revoke-seller'):
            c.execute('UPDATE users SET approved=? WHERE id=?',(int(args.command=='approve-seller'),user['id']))
        elif args.command=='grant-paid':
            if not 1<=args.days<=365:raise SystemExit('days must be 1..365')
            c.execute('INSERT INTO entitlements VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET paid_until=excluded.paid_until',(user['id'],time.time()+86400*args.days))
print('Updated.')
