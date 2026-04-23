// function myTest() {
//   clearTimeout(t);
//   var t;
//   t = setTimeout(log, 6000000000);
//   console.log(t);
//   // time is in milliseconds (1000 is 1 second)
// }
// function myTest1() {
//   console.log('idle #########')
//   var t;
//   window.onmousemove = resetTimer; // catches mouse movements
//   window.onmousedown = resetTimer; // catches mouse movements
//   window.onclick = resetTimer; // catches mouse clicks
//   window.onscroll = resetTimer; // catches scrolling
//   window.onkeypress = resetTimer; //catches keyboard actions


//   // function logout() {
//   //   console.log("check added");
//   //   inactivsession();
//   //   // localStorage.clear();
//   //   // localStorage.removeItem("token");
//   //   // localStorage.removeItem("user");
//   //   // localStorage.removeItem("usertoken");

//   //   window.location = "/#/login"; //Adapt to actual logout script
//   // }

//   function reload() {
//     window.location = self.location.href; //Reloads the current page
//   }

//   function resetTimer() {
//     clearTimeout(t);
//     t = setTimeout(logout, 600000);
//     // time is in milliseconds (1000 is 1 second)
//     //   t = setTimeout(reload, 3600000); // time is in milliseconds (1000 is 1 second)
//   }
//   // time is in milliseconds (1000 is 1 second)
// }

// function log() {
//   console.log("log");
// }

// function inactivsession() {
//   var tokens = "token " + getCookie("token");
//   console.log(tokens, "inactive");
//   //

//   fetch("/projectName/logout/", {
//     method: "GET", // or 'PUT'
//     headers: {
//       Authorization: tokens,
//     },
//   })
//     .then((response) => response)
//     .then((data) => {
//       console.log("Success:", data);
//     })
//     .catch((error) => {
//       console.error("Error:", error);
//     });
// }
// function idleTimer() {
//   console.log(localStorage.getItem("token").toString(), "tema ideal");
//   var t;
//   window.onmousemove = resetTimer; // catches mouse movements
//   window.onmousedown = resetTimer; // catches mouse movements
//   window.onclick = resetTimer; // catches mouse clicks
//   window.onscroll = resetTimer; // catches scrolling
//   window.onkeypress = resetTimer; //catches keyboard actions

//   // function logout() {
//   //   inactivsession();
//   //   // localStorage.clear();
//   //   // localStorage.removeItem("token");
//   //   // localStorage.removeItem("user");
//   //   // localStorage.removeItem("usertoken");

//   //   window.location = "/#/login";
//   //   const url = "/#/login";
//   //   //Adapt to actual logout script
//   //   // windowLocation(url);
//   // }
//   function windowLocation(url) {
//     console.log("window");
//     var X = setTimeout(function () {
//       window.location.replace(url);
//       return true;
//     }, 300);

//     if ((window.location = url)) {
//       clearTimeout(X);
//       return true;
//     } else {
//       if ((window.location.href = url)) {
//         clearTimeout(X);
//         return true;
//       } else {
//         clearTimeout(X);
//         window.location.replace(url);
//         return true;
//       }
//     }
//     return false;
//   }

//   function reload() {
//     window.location = self.location.href; //Reloads the current page
//   }

//   function resetTimer() {
//     clearTimeout(t);
//     t = setTimeout(logout, 600000); // time is in milliseconds (1000 is 1 second)
//     //   t = setTimeout(reload, 3600000); // time is in milliseconds (1000 is 1 second)
//   }
// }
// // idleTimer();

// function clearStorage() {
//   let session = sessionStorage.getItem('ref');
//   if (session == null) {
//       localStorage.clear();
//       var url = window.location.href;
//       console.log(url);
//       if(url == "http://localhost:4200/#/" || url == "http://services.docullyvdr.com/#/") {
//         console.log('run...')
//       } else {
//         console.log('djhsjdhsjdhjshd')
//         window.location.href = ''
//       }
//   }
//   sessionStorage.setItem('ref', 1);
// }
// window.addEventListener('load', clearStorage);

// document.addEventListener("visibilitychange", function () {
//   var timeout;
//   if (document.hidden) {
//     console.log("I'm away");
//     function logoutFunction() {
//       // your function for too long inactivity goes here
//       console.log("check added");
//       localStorage.clear();
//       localStorage.removeItem("token");
//       localStorage.removeItem("user");
//       localStorage.removeItem("usertoken");
//       sessionStorage.setItem("sessionClosed", "true");
//       window.location = "/#/"; //Adapt to actual logout script
//     }
//     if (timeout !== null) {
//         clearTimeout(timeout); // clear the previous one
//     }
//     timeout = setTimeout(logoutFunction, 3600000);
//     console.log('away -> ',timeout)
//   } else {
//     console.log("I'm here");
//     if(timeout){
//         clearTimeout(timeout);
//         timeout = null;
//         console.log('here -> ',timeout)
//     }
//   }
// });

// function idleLogout() {
//   if (window.location.href.includes('/documents') || window.location.href.includes('/folder_detail')) {
//     return;
//   }
//   var t;
//   window.onload = resetTimer;
//   window.onmousemove = resetTimer;
//   window.onmousedown = resetTimer;  // catches touchscreen presses as well      
//   window.ontouchstart = resetTimer; // catches touchscreen swipes as well 
//   window.onclick = resetTimer;      // catches touchpad clicks as well
//   window.onkeydown = resetTimer;
//   window.addEventListener('scroll', resetTimer, true); // improved; see comments

//   function yourFunction() {
//     // alert('Logout')
//     // your function for too long inactivity goes here
//     console.log("check added");
//     localStorage.clear();
//     localStorage.removeItem("token");
//     localStorage.removeItem("user");
//     localStorage.removeItem("usertoken");

//     window.location = "/#/"; //Adapt to actual logout script
//   }

//   function resetTimer() {
//     // console.log(t)
//     clearTimeout(t);
//     t = setTimeout(yourFunction, 3600000);  // time is in milliseconds
//   }
// }

// idleLogout();