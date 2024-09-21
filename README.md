## CleverTap Campaign planner

---

### What 
This script does below 4 jobs at high level:
1. Gets the CleverTap campaigns scheduled between 1-2 hour from now. (for ex: if current time is 2pm, it fetches campaigns which are scheduled between 3pm-3:59pm)
2. Gets the userbase of each campaign by running headless automation
3. If a campaign's userbase exceeds the max-limit(for the time frame it was originally set to run), it computes the **earliest possible schedule time in the same 1 hour window**.
4. Sends a report on slack with the above computed preferred schedule time. The report also has a Notes column which mentions whether there was a change in time, or if could not find any time frame within 1 hour window.


### How to setup
1. Clone this repo
2. Add `.env` file with the required values
3. In CLI, run `sh script.sh` / `./script.sh`
4. To setup crontab:
   1. In CLI, run `crontab -e`
   2. Add `0 6-22  * * * sh $HOME/clevertap-campaign-planner/script.sh` and save (this will run the script at the start of every hour between 6AM-10PM)
   3. Verify crontab using `crontab -l`

---