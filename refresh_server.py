import git
import subprocess
import time

repo = git.Repo('./')

while True:
    current = repo.head.commit
    try:
        repo.remotes.origin.pull()
    except git.GitCommandError:
        pass
    if current != repo.head.commit:
        print("Nouvelle version trouvée\nRedémarrage des services")
        subprocess.run(["systemctl", "restart", "nginx"])
        subprocess.run(["systemctl", "restart", "uwsgi.service"])
        print("It's all good man")
    time.sleep(10)
