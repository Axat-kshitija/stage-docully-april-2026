const msalParams = {
    auth: {
        authority: "https://login.microsoftonline.com/consumers",
        clientId: "4b856fc8-fba1-4773-9c32-06a90df43218",
        redirectUri:'https://services.docullyvdr.com'
        //redirectUri: "http://localhost:4200"
    },
}

const app = new msal.PublicClientApplication(msalParams);

async function getToken() {

    let accessToken = "";

    authParams = { scopes: ["OneDrive.ReadWrite"] };

    try {

        // see if we have already the idtoken saved
        const resp = await app.acquireTokenSilent(authParams);
        accessToken = resp.accessToken;

    } catch (e) {

        // per examples we fall back to popup
        const resp = await app.loginPopup(authParams);
        app.setActiveAccount(resp.account);

        if (resp.idToken) {

            const resp2 = await app.acquireTokenSilent(authParams);
            accessToken = resp2.accessToken;

        }
    }

    return accessToken;
}