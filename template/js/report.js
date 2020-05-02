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
  list += `<button class="btn btn-secondary mt-5" id="timeline-btn">Timeline chart</button>`
  list += `<button class="btn btn-secondary mt-1" id="media-btn">Media</button>`
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




function renderTimeline(){
  console.log("entrou");

  report = getReportData();
  console.log(report);
  // let first_date = new Date(report["timeline"][0]["timestamp"]*1000).toLocaleDateString("pt-PT")
  // let last_date = new Date(report["timeline"][report["timeline"].length-1]["timestamp"]*1000).toLocaleDateString("pt-PT")
  let entrys = Object.keys(report["timeline"]).length
  // console.log(last_date)

  content = getHeader("timeline")
  
  content+= `<div class="row"><div class="tracking-list">` 
  



    report["timeline"].forEach(item => {
      let date ="";
      let time ="";
      if(item["timestamp"] == 0){
        date = `<span class="badge badge-pill badge-danger text-white ml-3">Invalid date</span>`
        time = ``
      }else{
        timestamp = new Date(item["timestamp"] * 1000);
        date = timestamp.toLocaleDateString("pt-PT");
        time = timestamp.toLocaleTimeString("pt-PT");
      }

    content += ` <div class="tracking-item">
    <div class="tracking-icon status-intransit"> 
    <object data="svg/${item["event"]}.svg" type="image/svg+xml" class="w-100"></object>
    
    
    
    </div>
    <div class="tracking-date">${date}<span>${time}</span></div>
    <div class="tracking-content">`

    Object.keys(item["value"]).forEach(function (body) {
      content += `<span><strong>${body + ": </strong>" + item["value"][body]}</span>`;
    });
      
     
    
    
    

    content+=`</div></div>`

  });

  content += `</div></div></div></div>`
  
  $("#page-builder").html(content);

}

function getHeader(title){
  return `<div class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"><h1 class="h2">${capitalize(title)}</h1></div>`
}
 

function renderMedia(){
//   content = `<div class="embed-responsive embed-responsive-21by9">
//   <iframe class="embed-responsive-item" src="C:\\Users\\josef\\Desktop\\Autopsy_tests\\asdasd\\ModuleOutput\\AndroidForensics\\com.zhiliaoapp.musically\\2\\report\\Contents\\external\\cache\\welcome_screen_video4.mp4"></iframe>
// </div>`;

src = `C:\\Users\\josef\\Desktop\\Autopsy_tests\\test.mp4`

content = `
${getHeader("Media")}
<div class="row">
  <div class="col-lg-4 col-md-12 mb-4">
    <div class="embed-responsive embed-responsive-4by3 z-depth-1-half">
      <iframe class="embed-responsive-item" src="${src}" allowfullscreen></iframe>
    </div>
  </div>
</div>`

$("#page-builder").html(content);

}


function pageBuilder(title){
  report = getReportData()
  if (!(title in report)){
    return;
  }

  let content = "";

  content += getHeader(title)

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
  // renderMedia()
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
  $(".timeline-btn").on("click", renderTimeline);
  $("#reports-list").change(startUp);
  
}())

