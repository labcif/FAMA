/* globals Chart:false, feather:false */

function capitalize(text){
  return text.charAt(0).toUpperCase() + text.substr(1).toLowerCase();
}

function initializeReports(){
  Object.keys(reportData).forEach(function (item) {
    $("#reports-list").append(new Option(item, item));
  });
}

function getSelectedOption(select){
  return $(select).find(":selected").text()
}

function getReportData(){
  return reportData[getSelectedOption("#reports-list")];
}

function initializeMenus(){
  let list = "";

  Object.keys(getReportData()).forEach(function (item) {
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

  console.log(idName);

  Object.keys(getReportData()).forEach(function (item) {
    $("#menulink-" + item).removeClass("active");
  });

  $("#" + idName).addClass("active");

  let name = idName.replace("menulink-", "")
  pageBuilder(name);
}

function pageBuilder(title){
  report = getReportData()
  if (!(title in report)){
    return;
  }

  let content = "";

  content += `<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"><h1 class="h2">${capitalize(title)}</h1></div>`

  //Array of objects
  if (Array.isArray(report[title]) && typeof report[title][0] === 'object'){
    let titleDefined = false;
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;

    report[title].forEach(item => {
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
  else if (Array.isArray(report[title]) && typeof report[title][0] === 'string'){
    content += `<ul class="list-group">`;
    report[title].forEach(item => {
      content += `<li class="list-group-item">${item}</li>`;
    });
    content += `</ul>`;
  }
  //Object (key/value)
  else if (typeof report[title] === 'object'){
    content += `<div class="table-responsive"><table class="table table-striped table-sm table-bordered table-hover">`;


    Object.keys(report[title]).forEach(function (key) {
      content += `<tr><td>${key}</td><td>${report[title][key]}</td></tr>`;
    });

    content += `</tbody></table></div>`;

  }

  $("#page-builder").html(content);
}

function startUp(){
  initializeMenus()
  //generatedDate()

  let defined = false
  Object.keys(reportData).forEach(function (item) {
    if (!defined && item !== "header"){
      menuClick(item);
      defined = true;
    }
  });

  feather.replace()
}

(function () {
  'use strict'
  initializeReports()

  startUp()

  $(".menu-item").on("click", menuClick);
  $("#reports-list").change(startUp);

}())
