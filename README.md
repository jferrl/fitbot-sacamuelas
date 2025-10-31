# FitBot

Python script to automate your session bookings in [aimharder.com](http://aimharder.com) platform

## Usage

Having docker installed you only need to do the following command:

### Recommended: With precise timing (zero delay)
```bash
docker run -e email=your.email@mail.com -e password=1234 -e booking-goals={'\"0\":{\"time\":\"1815\"\,\"name\":\"Provenza\"}'} -e box-name=lahuellacrossfit -e box-id=3984 -e hours-in-advance=46 -e wait-for-exact-time=true pablobuenaposada/fitbot
```

### Legacy: Without precise timing
```bash
docker run -e email=your.email@mail.com -e password=1234 -e booking-goals={'\"0\":{\"time\":\"1815\"\,\"name\":\"Provenza\"}'} -e box-name=lahuellacrossfit -e box-id=3984 -e days-in-advance=3 pablobuenaposada/fitbot
```
Explanation about the fields:

`email`: self-explanatory

`password`: self-explanatory

`booking_goals`: expects a json where as keys you would use the day of the week as integer from 0 to 6 (Monday to Friday) and the value should be the time (HHMM) of the class and the name of the class or part of it.
Unfortunately this structure needs to be crazy escaped, but here's an example:

Mondays at 18:15 class name should contain ARIBAU
Wednesdays at 18:15 class name should contain ARIBAU
```python
{
  "0": {"time":"1815", "name":"ARIBAU"},
  "2": {"time":"1815", "name":"ARIBAU"}
}
```
which should be sent in this form:
```sh
{'\"0\":{\"time\":\"1815\"\,\"name\":\"ARIBAU\"}\,\"2\":{\"time\":\"1815\"\,\"name\":\"ARIBAU\"}'}
```

`box-name`: this is the sub-domain you will find in the url when accessing the booking list from a browser, something like _https://**lahuellacrossfit**.aimharder.com/schedule_

`box-id`: it's always the same one for your gym, you can find it inspecting the request made while booking a class from the browser:

<img src="https://raw.github.com/pablobuenaposada/fitbot/master/inspect.png" data-canonical-src="https://raw.github.com/pablobuenaposada/fitbot/master/inspect.png" height="300" />

`days-in-advance`: *(deprecated, use `hours-in-advance`)* This is how many days in advance the script should try to book classes from, so for example, if this script is being run on a Monday and this field is set to 3 it's going to try book Thursday class from `booking_goals`

`hours-in-advance`: **Recommended**. This is how many hours in advance the script should try to book classes. For example, if set to 46, it will book classes exactly 46 hours before they start. This provides more precise control than `days-in-advance`. Supports decimal values (e.g., 46.5 for 46 hours and 30 minutes).

`wait-for-exact-time`: Optional (default: false). When set to `true`, the script will calculate the exact moment when the booking window opens and wait until that precise time before attempting to book. This is the **recommended approach** for zero-delay bookings. Schedule your cron job to trigger 1-2 minutes before the booking window opens, and the script will handle the precise timing internally.

`family-id`: Optional. This is the id for the person who wants to book a class in case the account has more than one member. 
The value for this parameter can be found by inspecting the requests with the browser, as with the field `box-id`.

`proxy`: Optional. If you want to use a proxy, you can set it with the format `socks5://ip:port`.

## 🚨 Proxy note 🚨
It appears that AimHarder has started blocking connections by returning a 403 error based on the IP address location. If you are running this script from outside Spain, you may encounter these errors, which is why the proxy argument has been added.

The United States seems to be heavily blocked (possibly only Azure IPs), so running this script from GitHub Actions will likely fail without a proxy. While this is not confirmed, it seems AimHarder doesn't like the use of automated scripts, especially when run for free via GitHub Actions 😀. If you choose this approach, ensure you use a proxy that is not blocked by AimHarder.

**Note:** Use free proxies at your own risk, as your credentials will be transmitted through them. Additionally avoid sharing the proxy you are using in here since AimHarder may block it.

## I'm a cheapo, can I run this without using my own infrastructure for free?
Yes, you can! By using GitHub Actions, you can run this script without needing your own infrastructure. It can also be configured to run automatically on a schedule. For details about potential connection blocks and proxy usage, refer to the previous section.

You can find an example of the GitHub Actions workflow in the [`.github/workflows/schedule.yml`](.github/workflows/schedule.yml) file.

Clone this repo, get a proxy (https://www.freeproxy.world/), add your secrets, edit the file to your needs and it should be ready to go.

## 🎯 Pro Tip: Zero-Delay Bookings with Precise Timing

For the best booking experience with **zero delays**, use the new precise timing feature:

1. **Set up your cron trigger**: Configure your cron app or GitHub Actions to trigger **1-2 minutes before** the booking window opens.
   - Example: If booking opens at 10:00:00, trigger at 09:58:00

2. **Enable precise timing**: Use `wait-for-exact-time=true` in your configuration

3. **How it works**: 
   - The script calculates the exact booking window opening time (e.g., Monday 08:00 class → booking opens Saturday 10:00 for 46h advance)
   - Waits internally until that precise moment (within seconds)
   - Executes the booking immediately when the window opens

**Example workflow for 46-hour advance booking (opens at 10:00 AM):**
```yaml
hours_in_advance: 46
booking_goals_raw: '{"0":{"time":"0800","name":"CrossFit"}}'
# In Docker run command:
-e "hours-in-advance=46"
-e "wait-for-exact-time=true"
```

**Cron schedule (trigger at 09:58 AM):**
```
58 9 * * * /path/to/trigger-script.sh
```

This approach eliminates all delays and ensures you're booking at the exact millisecond the window opens! 🚀

Enjoy!
