# Project 2 - Auth0 Implementation: Step-by-Step Guide

Files in this folder: `api_server.py`, `pkce_login.py`, `rotation_test.py`, `post_login_action.js`, `config.py`, `.env.example`, `requirements.txt`.
All commands run in the Codespaces terminal, in this folder.

## 0. One-time setup (GitHub Codespaces)
1. On github.com create a **private** repository (e.g. `securenova-p2`) and upload this folder's files (drag them in on the "Add file > Upload files" page, then commit).
2. Click **Code > Codespaces > Create codespace on main**. A VS Code editor opens in your browser with Python ready.
3. In its terminal run: `pip install -r requirements.txt` then `cp .env.example .env`, and fill in `.env` as you go (steps 1-2 below).
4. `.gitignore` keeps `.env` and `tokens.json` out of the repo. Never commit or screenshot them.
5. Use two terminals: one runs `python api_server.py` (leave it running), the other (the **+** icon) runs the other scripts.
6. Codespaces stops after about 30 minutes idle; your files stay. Reopen it from github.com/codespaces.

## 1. Auth0 tenant and applications (Screenshot 1)
1. Sign up free at auth0.com, create a tenant (e.g. `securenova-dev`). Note the domain, e.g. `dev-abc123.us.auth0.com`, and put it in `.env` as `AUTH0_DOMAIN`.
2. **Applications > Create Application** -> name `SecureNova AI Chat` -> **Regular Web Applications**. Settings tab:
   - Allowed Callback URLs: `http://localhost:3000/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins (this is the CORS list) and Allowed Origins (CORS): `http://localhost:3000`
   - Advanced Settings > Grant Types: tick **Authorization Code** and **Refresh Token**; untick Implicit. Save.
   - Copy Client ID and Client Secret into `.env` (`WEB_CLIENT_ID`, `WEB_CLIENT_SECRET`).
3. **Create Application** -> `SecureNova AI Agent` -> **Machine to Machine Applications**. When asked, pick the API from step 2.1 below (or authorise it after creating the API) and tick only `read:ai-data`. Advanced Settings > Grant Types: only **Client Credentials**. M2M apps have no callback URLs or browser CORS, so there is nothing to set; say so in your write-up. Copy ID and secret into `.env` (`M2M_*`).
4. For the SSO check, create a third Regular Web App `SecureNova Support Portal` with the same callback and origins. Copy into `WEB2_*`. The brief asks for two apps, and this is only a helper for the SSO proof.
5. **Screenshot 1:** Applications list showing both `SecureNova AI Chat` (Regular Web) and `SecureNova AI Agent` (Machine to Machine).

## 2. API with two scopes (Screenshot 2) and PKCE flow
1. **Applications > APIs > Create API**: Name `SecureNova AI API`, Identifier `https://api.securenova.local`, Signing Algorithm **RS256**.
2. API > **Permissions** tab: add `read:ai-data` ("Read AI chat data, user level") and `write:admin` ("Admin write, admin level").
3. API > **Settings**: leave RBAC off (simplest), so the scopes you request are the scopes you get. Set **Token Expiration (seconds)** to `60` here for the credential-rotation test in step 4. Save.
4. **Screenshot 2:** the API's Permissions tab showing both scopes.
5. Start the API in one terminal: `python api_server.py`
6. In a second terminal: `python pkce_login.py`
   - The script prints a link. Open it in your own browser, sign up or log in, and accept the consent screen if it shows up.
   - Afterwards the browser says "This site can't be reached" on `localhost:3000`. That is expected: copy the full address from the address bar and paste it into the terminal.
   - The script saves the tokens and calls the API: `/chat` returns **200** and `/admin` returns **403**. That is your "user-level token is rejected" proof. Keep this terminal output for your report.
7. Paste the `access_token` from `tokens.json` into https://jwt.io and check: header `alg` = RS256, `aud` = your API identifier, `iss` = `https://<your domain>/`, `exp` in the future, `scope` = `read:ai-data`.

## 3. MFA and Attack Protection (Screenshots 5 and 7)
1. **Security > Multi-factor Auth:** switch on **One-time Password** and turn the other factors off. Under *Define policies*, choose **Always** (require MFA).
2. Log in again with `python pkce_login.py`. Auth0 shows the enrolment screen (QR code) the first time and the 6-digit challenge on later logins. Use an authenticator app (Google/Microsoft Authenticator). **Screenshot 5:** the enrolment screen or the TOTP challenge. Blur the QR code.
3. **Security > Attack Protection > Brute-force Protection:** toggle on, **Max attempts = 10**, keep the "Block" shield on. **Suspicious IP Throttling:** toggle on, keep the default thresholds and shields.
4. **Screenshot 7:** Attack Protection page showing both toggles ON. Scroll so both are visible; zoom out if needed.
5. Note for your report: the brief says "15-minute lockout", but I'm not aware of a lockout-minutes field on this panel. As far as I know Auth0 blocks the user until they follow the unblock email link, an admin unblocks them, or the password is changed. Check your panel; if there is no field, say that in the report and don't invent a setting.

## 4. Credential rotation script (Screenshot 8)
1. Make sure the API token lifetime is 60 seconds (step 2.3) and `api_server.py` is running.
2. Run: `python rotation_test.py`
3. It gets an M2M token, calls `/chat` (**200 OK**), waits 65 seconds, replays the same token and gets **401 Unauthorized**. Every line has a timestamp.
4. **Screenshot 8:** the terminal showing the timestamped 200 then 401 and the `PASS` line.

## 5. Post-login Action, claim and SSO (Screenshots 3 and 6)
1. **Actions > Library > Build Custom > Create Action**: Name `Add agent_id claim`, Trigger **Login / Post Login**, runtime Node 22 (or the default).
2. Paste in `post_login_action.js` and click **Deploy**.
3. **Actions > Triggers > post-login:** drag your custom action between **Start** and **Complete**, then **Apply**. If you skip this step the claim never appears.
4. **Screenshot 6:** the Actions editor with the code showing the `agent_id` claim lines.
5. Run `python pkce_login.py` again. Paste the new `access_token` from `tokens.json` into jwt.io. **Screenshot 3:** decoded payload with `aud`, `iss`, `exp`, `scope` and the `agent_id` claim all in view.
6. **SSO check:** with the browser still logged in from the last run, run `python pkce_login.py --client web2`. If it prints "Login OK" and no login screen appears, the second client accepted the existing session without re-authentication.

## 6. Universal Login branding (Screenshot 4)
**Branding > Universal Login > Customization (Colors and Fonts / Page Background):** upload a logo URL (any public image URL), set primary colour and page background (e.g. dark navy and a teal button), save. Then run `python pkce_login.py`, open its link and screenshot the login page with the URL bar visible.

## Screenshot checklist (in the same order as the brief)
1. Applications page: Regular Web App + M2M app.
2. APIs page: `read:ai-data` and `write:admin`.
3. jwt.io: decoded JWT with aud, iss, exp, scope, agent_id.
4. Universal Login page with custom branding.
5. MFA enrolment or TOTP challenge.
6. Actions editor with agent_id code.
7. Attack Protection: Brute-force + Suspicious IP both ON.
8. Terminal: rotation script 200 then 401, timestamped.

The brief's heading says 9 screenshots but I could only see 8 items. Scroll that list again and check for a ninth.

## Quick fixes
- `redirect_uri mismatch`: callback in the app settings must be exactly `http://localhost:3000/callback`.
- `access_denied` / "client is not authorized": authorise the M2M app on the API (APIs > your API > Machine to Machine Applications).
- `/admin` returned 200: you requested `write:admin` or turned RBAC on and gave the user that permission. Re-run with the default scope.
- API shows `invalid_token`: check `API_AUDIENCE` in `.env` matches the API identifier exactly and `AUTH0_DOMAIN` has no `https://`.
- `agent_id` missing: the Action is not dragged into the Login flow or not deployed.
- "This site can't be reached" after login: expected. Just paste the address bar URL back into the terminal.
