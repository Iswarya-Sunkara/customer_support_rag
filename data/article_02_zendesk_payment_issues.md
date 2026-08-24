# Troubleshooting common payment issues

Source: Zendesk
URL: https://support.zendesk.com/hc/en-us/articles/9317629048730-Troubleshooting-common-payment-issues
Category: Payment

Your payment may fail for a few reasons. This article describes common payment issues and how to resolve them.

This article contains the topics below:

- Credit card declined
- Credit card payment fails
- I don't see the forms to update the payment method
- Authenticate 3D secure payments
- Other common customer payment issues

### Credit card declined

### Symptoms

I try to submit my credit card details, but I receive a generic error such as Your credit card was declined.

### Resolution

- See [Resolve payment errors](https://support.zendesk.com/hc/en-us/articles/4408832461210-Resolving-issues-when-your-credit-card-fails#h_fbf65747-a573-41f1-a94e-3e232da412c0) for the full list of card rejection reasons
- Move to section Other common customer payment issues for next steps
- If you try to add a pre-paid credit card, it may fail due to local policies. If this happens, try to add a different payment method such as PayPal, ACH, or a different credit card.
- If all other fix steps fail, reach out to the issuing bank to confirm the card is available to use for purchases

### Credit card payment fails

### Symptoms

I successfully added my credit card to my account, but the payment failed.

### Resolution

This can happen for a variety of reasons:

- Insufficient funds, or transaction amount above limit
- Card expiration
- Card deactivated or replaced
- High-risk transaction determined by the payment processor and issuing bank

To solve this issue:

- See [Resolve issues when your credit card fails](https://support.zendesk.com/hc/en-us/articles/4408832461210-Resolving-issues-when-your-credit-card-fails) for the full list of reasons of a card rejection
- In many cases, Zendesk doesn't receive details of a payment rejection. If this is the case, reach out to the issuing bank of the credit card for full details of the payment failure.
- If available, try a different payment method, such as PayPal, ACH, or a different credit card
- If all else fails, reach out to [Zendesk customer support](https://support.zendesk.com/hc/en-us/articles/4408843597850-Contacting-Zendesk-customer-support) to resolve the issue

### I don't see the forms to update the payment method

### Symptoms

I followed the instructions in [Manage payments](https://support.zendesk.com/hc/en-us/articles/4408821572506-Managing-payments), but I don't see the forms to update the payment method.

### Resolution

- You don't have [account owner](https://support.zendesk.com/hc/en-us/articles/4408822084634-Finding-and-changing-the-account-owner) permissions. Reach out to the account owner on your account to update your payment method.
- Your account isn't eligible to self-manage your payment, and you need assistance from an account representative or Zendesk Sales. In this case, you won't see the edit button under the Payment method section. Instead, contact your account representative or [Zendesk Customer Support](https://support.zendesk.com/hc/en-us/articles/4408843597850-Contacting-Zendesk-customer-support) to resolve the issue.

### Authenticate 3D secure payments

### Understand the terminology

Strong Customer Authentication (SCA):

- Regulatory requirement in Europe under the PSD2 directive
- Requires two-factor authentication for online payments
- Mandated by law in certain jurisdictions

3D Secure (3DS):

- Technical protocol that implements SCA requirements
- Version 2.0 is current standard
- Provides the authentication mechanism

SCA is the requirement, and 3DS is the implementation.

### How 3D secure verification works

1. You initiate payment to Zendesk
2. The payment processor contacts your card issuer or bank
3. The bank determines if SCA verification is required
4. If required, you are redirected to complete verification using a mobile app notification, SMS code, or biometric authentication
5. After successful verification, the payment processes

### Troubleshoot 3DS issues

Payment fails at the verification step due to common causes:

- A pop-up blocker blocks the verification window. Temporarily allow pop-ups for zendesk.com and the payment processor domain. Check the browser address bar for a blocked pop-up icon.
- An interrupted connection means communication failed between Zendesk, the payment processor, and the bank. Check for a stable internet connection and retry the payment.
- The bank declined the verification. This can happen due to a wrong verification code, too many attempts, or the bank flags the transaction as suspicious. Contact your bank to verify the payment is allowed.
- For browser compatibility, try a different browser such as Chrome, Firefox, or Edge. Ensure JavaScript is enabled and disable ad blockers temporarily.

If the verification window doesn't appear:

- Check the browser console for errors in the F12 Console tab
- Disable browser extensions temporarily
- Clear browser cache and cookies
- Try incognito or private browsing mode
- Verify payment processor domains are not blocked by a corporate firewall, antivirus software, or DNS filter

### Cross-reference with browser issues

Many 3DS failures are caused by pop-up blockers mentioned in the browser fix section. Try those solutions first.

### Get help

If the payment consistently fails:

- Contact your bank to verify online payments are enabled
- Ensure international transactions are allowed if applicable
- Contact Zendesk Support with your browser type and version, a screenshot of the error and hide sensitive card details, and the approximate time of the failed attempt

### Other common customer payment issues

### Symptoms

My payment method fails to save for unknown reasons, or the form times out with no response.

### Resolution

This could be an indication of a client-side or browser issue that can happen for a variety of reasons, where the content blocks or interferes with the authorization of the new payment method:

- Your browser blocks pop-ups. Sometimes this will display up as a warning message in the browser's address bar, or as a dialog box.
- The extensions, plugins, or VPN block network traffic

To solve this issue:

- Clear the browser cache and cookies
- Try from a different browser. This can help confirm if it’s not a problem with the browser configuration and provides a quick workaround.
- Try from a different device entirely. This can help confirm that it’s not a problem with the network configuration on the original device.
- After the issue is resolved, be sure to restore all your necessary network security safeguards
