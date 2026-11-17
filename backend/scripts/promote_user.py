"""Local-only role administration. Run from backend with an email and role."""
import argparse
from app.db import connect, init_db

def main():
    parser=argparse.ArgumentParser(description='Promote a registered account to faculty/admin (local trusted shell only).')
    parser.add_argument('email'); parser.add_argument('role',choices=['student','faculty','admin'])
    args=parser.parse_args(); init_db()
    with connect() as db:
        cur=db.execute('UPDATE users SET role=? WHERE email=?',(args.role,args.email.lower()))
        if cur.rowcount==0: raise SystemExit('No account found for that email. Register the account first.')
    print(f'Updated {args.email} role to {args.role}. Sign out and sign back in to refresh your token.')
if __name__=='__main__':main()
