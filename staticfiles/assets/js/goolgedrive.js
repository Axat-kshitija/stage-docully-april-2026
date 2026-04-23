
const SCOPES = 'https://www.googleapis.com/auth/drive.readonly';

// TODO(developer): Set to client ID and API key from the Developer Console
//stagging
//const CLIENT_ID = "872398678576-1fdler6no32582r40ulbr6e5i6mnvlm9.apps.googleusercontent.com" 
//local
const CLIENT_ID = '872398678576-f3kq2neklc2ngb1bur5dcshufjebh0n4.apps.googleusercontent.com';
const API_KEY = 'AIzaSyAlfZeiPFGf42dYL2hVbBuFn1a8IKLdjnQ';
const APP_ID = 'docullyvdr-419813';


// TODO(developer): Replace with your own project number from console.developers.google.com.
let tokenClient;
let accessToken = null;
let pickerInited = false;
let gisInited = false;


//document.getElementById('authorize_button').style.visibility = 'hidden';
//document.getElementById('signout_button').style.visibility = 'hidden';

/**
 * Callback after api.js is loaded.
 */
function gapiLoaded() {
  gapi.load('client:picker', initializePicker);
}

/**
 * Callback after the API client is loaded. Loads the
 * discovery doc to initialize the API.
 */
async function initializePicker() {
  await gapi.client.load('https://www.googleapis.com/discovery/v1/apis/drive/v3/rest');
  pickerInited = true;
  maybeEnableButtons();
}

/**
 * Callback after Google Identity Services are loaded.
 */
function gisLoaded() {
  tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: CLIENT_ID,
    scope: SCOPES,
    callback: '', // defined later
  });
  gisInited = true;
  maybeEnableButtons();
}

/**
 * Enables user interaction after all libraries are loaded.
 */
function maybeEnableButtons() {
  if (pickerInited && gisInited) {
   // document.getElementById('authorize_button').style.visibility = 'visible';
  }
}

/**
 *  Sign in the user upon button click.
 */
function handleAuthClick() {
  tokenClient.callback = async (response) => {
    if (response.error !== undefined) {
      throw (response);
    }
    accessToken = response.access_token;
    document.getElementById('signout_button').style.visibility = 'visible';
    document.getElementById('authorize_button').innerText = 'Connect to Google Drive';
    await createPicker();
  };

  if (accessToken === null) {
    // Prompt the user to select a Google Account and ask for consent to share their data
    // when establishing a new session.
    tokenClient.requestAccessToken({ prompt: 'consent' });
  } else {
    // Skip display of account chooser and consent dialog for an existing session.
    tokenClient.requestAccessToken({ prompt: '' });
  }
}

/**
 *  Sign out the user upon button click.
 */
function handleSignoutClick() {
  if (accessToken) {
    accessToken = null;
    google.accounts.oauth2.revoke(accessToken);
    document.getElementById('content').innerText = '';
    document.getElementById('authorize_button').innerText = 'Connect to Google Drive';
    document.getElementById('signout_button').style.visibility = 'hidden';
  }
}

/**
 *  Create and render a Picker object for searching images.
 */
function createPicker() {
  const view = new google.picker.View(google.picker.ViewId.DOCS);
  //view.setMimeTypes('image/png,image/jpeg,image/jpg');
  const picker = new google.picker.PickerBuilder()
    .enableFeature(google.picker.Feature.NAV_HIDDEN)
    .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
    .setDeveloperKey(API_KEY)
    .setAppId(APP_ID)
    .setOAuthToken(accessToken)
    .addView(view)
    .addView(new google.picker.DocsUploadView())
    .setCallback(pickerCallback)
    .build();
  picker.setVisible(true);
}

/**
 * Displays the file details of the user's selection.
 * @param {object} data - Containers the user selection from the picker
 */
async function pickerCallback(data) {
  if (data.action === google.picker.Action.PICKED) {
    let text = `Picker response: \n${JSON.stringify(data, null, 2)}\n`;
    const document = data[google.picker.Response.DOCUMENTS][0];
    const fileId = document[google.picker.Document.ID];
    console.log(data.docs)
    var files = data.docs;
    localStorage.setItem('googletoken',JSON.stringify(accessToken))
    window.GoogleDriveFunction(files);
  }

  // function downloadFile(fileId) {
  //   var accessToken = gapi.auth.getToken().access_token;
  //   var xhr = new XMLHttpRequest();
  //   xhr.open('GET', 'https://www.googleapis.com/drive/v3/files/' + fileId + '?alt=media');
  //   xhr.setRequestHeader('Authorization', 'Bearer ' + accessToken);
  //   xhr.responseType = 'blob';
  //   xhr.onload = function () {
  //     var url = window.URL.createObjectURL(xhr.response);
  //     var a = document.createElement('a');
  //     a.href = url;
  //     a.download = 'filename'; // Set desired filename here
  //     document.body.appendChild(a);
  //     a.click();
  //     window.URL.revokeObjectURL(url);
  //   };
  //   xhr.send();

  // }

}

