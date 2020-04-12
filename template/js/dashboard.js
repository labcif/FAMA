/* globals Chart:false, feather:false */

function capitalize(text){
  return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
}

function initializeMenus(){
  let list = "";

  Object.keys(reportData).forEach(function (item) {
    if (item !== "header"){
      list += `<li class="nav-item"><a id="menulink-${item}" class="nav-link menu-item" href="#"><span data-feather="file-text"></span>${capitalize(item)}</a></li>`;
    }
  });
  
  $("#menu-list").html(list);
}

function generatedDate(){
  $("#generated-date").html("Generated at " + (new Date(Number(reportData["header"]["report_date"])).toISOString().slice(0, 19).replace(/-/g, "/").replace("T", " ")));
}

function menuClick(event){
  if (event.target){
    idName = event.target.id;
  }
  else{
    idName = "menulink-" + event;
  }

  Object.keys(reportData).forEach(function (item) {
    $("#menulink-" + item).removeClass("active");
  });

  $("#" + idName).addClass("active");

  let name = idName.replace("menulink-", "")
  pageBuilder(name);
}

function pageBuilder(title){
  if (!(title in reportData)){
    return;
  }

  let content = "";

  content += `<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"><h1 class="h2">${capitalize(title)}</h1></div>`

  //Array of objects
  if (Array.isArray(reportData[title]) && typeof reportData[title][0] === 'object'){
    let titleDefined = false;
    content += `<div class="table-responsive"><table class="table table-striped table-sm">`;

    reportData[title].forEach(item => {
      //define table header
      if (!titleDefined){
        let theads = ""
        Object.keys(item).forEach(function (head) {
          theads += `<td>${head}</td>`;
        });
        titleDefined = true;

        content += `<thead><tr>${theads}</tr></thead><tbody>`
      }

      content += `<tr>`;
      Object.keys(item).forEach(function (body) {
        content += `<td>${item[body]}</td>`;
      });
      content += `</tr>`;
    })

    content += `</tbody></table></div>`;
  }
  //Array of strings
  else if (Array.isArray(reportData[title]) && typeof reportData[title][0] === 'string'){
    content += `<ul class="list-group">`;
    reportData[title].forEach(item => {
      content += `<li class="list-group-item">${item}</li>`;
    });
    content += `</ul>`;
  }
  //Object (key/value)
  else if (typeof reportData[title] === 'object'){
    content += `<div class="table-responsive"><table class="table table-striped table-sm">`;


    Object.keys(reportData[title]).forEach(function (key) {
      content += `<tr><td>${key}</td><td>${reportData[title][key]}</td></tr>`;
    });

    content += `</tbody></table></div>`;

  }



  $("#page-builder").html(content);
}

(function () {
  'use strict'
  //Initialize menu
  initializeMenus()
  generatedDate()

  $(".menu-item").on("click", menuClick);
  
  //Select first item of menu
  let defined = false
  Object.keys(reportData).forEach(function (item) {
    if (!defined && item !== "header"){
      menuClick(item);
      defined = true;
    }
  });
  
  feather.replace()
}())
