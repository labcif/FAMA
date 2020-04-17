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

function getEventIcon(event){
  var icons ={}
  icons["video"] = `
  <svg x="0px" y="0px" viewBox="0 0 426.667 426.667">
  <g>
     <polygon points="170.667,309.333 298.667,213.333 170.667,117.333" />
     <path d="M213.333,0C95.467,0,0,95.467,0,213.333s95.467,213.333,213.333,213.333S426.667,331.2,426.667,213.333
     S331.2,0,213.333,0z M213.333,384c-94.08,0-170.667-76.587-170.667-170.667S119.253,42.667,213.333,42.667
     S384,119.253,384,213.333S307.413,384,213.333,384z" />
  </g>
  </svg>`;

  return icons[event];
}


function renderTimeline(){
  content = `<div class="container"><h2>TIMELINE</h2><div class="row"><div class="col-md-12 col-lg-12"><div id="tracking-pre"></div><div id="tracking"><div class="text-center tracking-status-intransit"><p class="tracking-status text-tight">in transit</p></div><div class="tracking-list">` 
  report = getReportData();

  report["timeline"].forEach(item => {
    d = new Date(item["timestamp"] * 1000);
    // console.log( d.toLocaleDateString("pt-PT") +" "+ d.toLocaleTimeString("pt-PT"))
    
    let date = d.toLocaleDateString("pt-PT");
    let time = d.toLocaleTimeString("pt-PT");

    content += ` <div class="tracking-item">
    <div class="tracking-icon status-intransit"> ${getEventIcon("video".toLowerCase())}
    </div>
    <div class="tracking-date">${date}<span>${time}</span></div>
    <div class="tracking-content">${item["value"]["event"]}`

    Object.keys(item["value"]).forEach(function (body) {
      content += `<span><strong>${body + ": </strong>" + item["value"][body]}</span>`;
    });
      
     
    
    
    

    content+=`</div></div>`

  });

  content += `</div></div></div></div></div>`
  
  $("#page-builder").html(content);

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
  renderTimeline()
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

