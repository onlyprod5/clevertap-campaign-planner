## CleverTap Campaign planner

### How to setup
1. Clone this repo
2. In CLI, run `sh script.sh` / `./script.sh`
3. To setup crontab:
   1. In CLI, run `crontab -e`
   2. Add `0 6-22  * * * sh $HOME/clevertap-campaign-planner/script.sh` and save (this will run the script at the start of every hour between 6AM-10PM)
   3. Verify crontab using `crontab -l`