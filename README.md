# Group A
This is the offical backend repository for Dii booking system of agile course

# Working principle：

## First time to access to repository:
1. git init 
2. git remote add origin url, note that u have a local branch master and remote branch main now
3. git pull origin main (This pull the code from main branch to local master)
4. git checkout main (This create a main branch at local, this is served as sync later)

## When u start writing code next time, you need to get code from main to sync:
1. git checkout main (This moves u to local main branch)
2. git pull (This update your local main)
3. git checkout master (This moves u to local master branch)
4. git merge main (This merge the lastest correct code of main to your developin branch master)
5. resolve conflit by adding or deleting code

## When u done coding ur work
1. git add .
2. git commit -m "write what u have done here, must write something meaningful here"
3. git push origin master  (note here push to master, cuz master is the working branch)

NB. master is the develop branch!!! But main is the authority branch.
    So push to master so i can review at repositroy, but pull from main so u get up to date correct code.