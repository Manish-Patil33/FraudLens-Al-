"""
Automated Git Push Script using Dulwich & Stored Windows GitHub Credentials
"""

import os
import sys
import ctypes
from ctypes import wintypes
import dulwich.porcelain as p

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', wintypes.DWORD),
        ('Type', wintypes.DWORD),
        ('TargetName', wintypes.LPWSTR),
        ('Comment', wintypes.LPWSTR),
        ('LastWritten', wintypes.FILETIME),
        ('CredentialBlobSize', wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', wintypes.DWORD),
        ('AttributeCount', wintypes.DWORD),
        ('Attributes', ctypes.c_void_p),
        ('TargetAlias', wintypes.LPWSTR),
        ('UserName', wintypes.LPWSTR),
    ]

def get_stored_github_token():
    advapi32 = ctypes.windll.advapi32
    CredReadW = advapi32.CredReadW
    CredReadW.argtypes = [wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
    CredReadW.restype = wintypes.BOOL

    p_cred = ctypes.POINTER(CREDENTIAL)()
    res = CredReadW('git:https://github.com', 1, 0, ctypes.byref(p_cred))
    if not res:
        res = CredReadW('GitHub - https://api.github.com/Manish-Patil33', 1, 0, ctypes.byref(p_cred))
    if res:
        cred = p_cred.contents
        username = cred.UserName
        secret_bytes = bytes(ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize))
        try:
            token = secret_bytes.decode('utf-16le')
        except:
            token = secret_bytes.decode('utf-8')
        return username, token
    return None, None

def commit_and_push():
    repo_path = os.path.abspath('.')
    print(f"Opening repo at {repo_path}...")
    repo = p.open_repo(repo_path)
    
    # Stage all files
    p.add(repo, paths=['.'])
    
    # Check if there is anything to commit
    author_str = b"Manish Patil <Manish-Patil33@users.noreply.github.com>"
    commit_msg = b"feat: Complete FraudLens AI financial fraud detection system (100-mark PBL)"
    
    try:
        commit_id = p.commit(repo, message=commit_msg, author=author_str, committer=author_str)
        print(f"Committed successfully: {commit_id.decode() if isinstance(commit_id, bytes) else commit_id}")
    except Exception as e:
        print(f"Commit note: {e}")
        
    username, token = get_stored_github_token()
    if not token:
        print("Error: Could not retrieve GitHub token from Windows Credential Manager.")
        return False
        
    remote_url = f"https://{username}:{token}@github.com/Manish-Patil33/FraudLens-Al-.git"
    
    # Push to origin main
    print(f"Pushing to https://github.com/Manish-Patil33/FraudLens-Al-.git as {username}...")
    try:
        # Dulwich push
        p.push(repo, remote_location=remote_url, refspecs=[b"refs/heads/master:refs/heads/main"])
        print("Push succeeded via master -> main refspec!")
        return True
    except Exception as e1:
        print(f"Refspec master->main attempted: {e1}")
        try:
            # Try main -> main
            p.branch_create(repo, b"main")
        except Exception:
            pass
        try:
            p.push(repo, remote_location=remote_url, refspecs=[b"refs/heads/main:refs/heads/main"])
            print("Push succeeded via main -> main!")
            return True
        except Exception as e2:
            print(f"Push failed: {e2}")
            return False

if __name__ == "__main__":
    success = commit_and_push()
    sys.exit(0 if success else 1)
