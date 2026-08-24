# Troubleshoot app issues in Zendesk account

Source: Zendesk
URL: https://support.zendesk.com/hc/en-us/articles/4408836095514-Troubleshoot-app-issues-in-Zendesk-account
Category: Troubleshooting

If your app doesn’t work as expected, follow these steps to identify and resolve the problem.

This article contains the topics below:

- Disable all apps
- Disable specific apps
- Clear the browser cache
- Check roles and permissions
- Check for console errors
- Still experience issues?

## Disable all apps

[Disable support apps for all agents](https://support.zendesk.com/hc/en-us/articles/4409155972378-Managing-your-installed-apps#topic_vk5_pn4_ym) or add `?noapps` to the end of the uniform resource locator (URL) of the ticket where the issue persists.

```text
https://yoursubdomain.zendesk.com/agent/tickets/12345?noapps
```

This step helps you determine if any app interferes with your account performance. If an app prevents you from using your account, contact the [app's developer](https://support.zendesk.com/hc/en-us/articles/4409155972378-Managing-your-installed-apps#topic_fgd_rmw_45) for further support.

## Disable specific apps

If you identify that the issue is with your apps, target the specific app. Activate and deactivate specific apps to pinpoint the app at fault:

- Append `?noapps=installation_id` to the URL to test with only that app deactivated. To retrieve the installation ID, use this application programming interface (API) endpoint: [List App Installations](https://developer.zendesk.com/api-reference/ticketing/apps/apps/#list-app-installations).
- Append `?app_ids=app_id` to the URL to test with only that app activated. To retrieve the app ID, see [How can I find an App ID in my Zendesk instance?](https://support.zendesk.com/hc/en-us/articles/4408845626522-How-can-I-find-an-App-ID-in-my-Zendesk-instance-)

## Clear the browser cache

Open your account in an incognito or private browser. If the issue disappears, clear the [browser cache and cookies](https://support.zendesk.com/hc/en-us/articles/4408823836314-How-to-clear-cache-and-cookies), then test again.

## Check roles and permissions

If only some agents experience issues, check their [roles and permissions](https://support.zendesk.com/hc/en-us/articles/4408882153882-Creating-custom-roles-and-assigning-agents). Agents without access to the app functionality experience problems.

## Check for console errors

Check the browser console for any errors. You can capture these errors in an HTTP Archive (HAR) file. The process to capture this information is unique for each browser. For more information, see [Generating a HAR file](https://support.zendesk.com/hc/en-us/articles/4408828867098-Generating-a-HAR-file-for-troubleshooting).

## Still experience issues?

If these steps don’t resolve the problem, contact [Zendesk Customer Support](https://support.zendesk.com/hc/en-us/articles/4408843597850-Contacting-Zendesk-Customer-Support) for further help, and include this information in your message:

- Time of when the issue began and its frequency
- A [HAR file](https://support.zendesk.com/hc/en-us/articles/4408828867098-Generating-a-HAR-file-for-troubleshooting) that captures the unexpected behavior
- The troubleshooting steps performed from this article
