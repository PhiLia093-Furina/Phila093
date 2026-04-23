
var url =['https://www.bilibili.com/video/BV1ADFNe5EAG/',
        'https://www.bilibili.com/video/BV16HPsezEgp/',
        'https://www.bilibili.com/video/BV16FQwYGE8k/',
        'https://www.bilibili.com/video/BV17YR2YuETG/',
        'https://www.bilibili.com/video/BV1AbLezxEKM/',
        'https://www.bilibili.com/video/BV1ZNEiz8ESM/',
        'https://www.bilibili.com/video/BV14nTNzfEcU/',
        'https://www.bilibili.com/video/BV1HfKiz3Ezf/',
        'https://www.bilibili.com/video/BV1otbGzXE5K/',
        'https://www.bilibili.com/video/BV1Hdh1zhE1e/',
        'https://www.bilibili.com/video/BV1r5nwzVEBg/',
        'https://www.bilibili.com/video/BV13KxrzDEE4/',
        'https://www.bilibili.com/video/BV19RhAzcEdU/',
        'https://www.bilibili.com/video/BV1yZ1MB1Eej/'];


var chrome = ["https://bing.com/search?q=",
              "https://www.baidu.com/s?wd=",
              "https://www.sogou.com/web?query="
];


function blind(){
        $('#search_input').on('keydown', function (e) {
        // 13 是回车键的编号
            if (e.keyCode === 13) {
                search(); // 直接调用你现有的搜索函数
            }
        });
}

$(function () {
        home();
        blind()
    });

function home(){
    $(".parent_win").empty(); // 清空

    // 填入你想显示的新内容
    var homeHtml = `
        <div class="Home">
            <div class = "home_title">
            欢迎来到首页
            </div>
            <div class="search_box">
                <input type="text" id="search_input" placeholder="搜索视频..." />
                <button class="search_btn" onclick="search()">
                搜索</button>
            </div>
        </div>`;

    $(".parent_win").html(homeHtml);
    blind()
}

function loadCard_Genshin(){
    $(".parent_win").empty();

    var homeHtml = `
        <div class="ys">
            <div class="ys_box">
                <button class="ys_btn" onclick=goToUrl('https://ys.mihoyo.com/')>
                原神官网</button>
                <button class="ys_btn" onclick=goToUrl('https://www.miyoushe.com/ys/')>
                米游社</button>
            </div>
        </div>`;

    $(".parent_win").html(homeHtml);
    blind()
}

function loadCard_HK(){
    $(".parent_win").empty();
    for (var i = 1; i <= 12; i++){
        var img = i + ".png";
        var link = url[i-1]
        var a = `
            <div class="card" style = "background-image:url('pic/${img}')">
                <button class="buttons" onclick="goToUrl('${link}')">播放</button>
            </div>`;
        $(".parent_win").append(a);
    }
        
        a = `
        <div class="last1">
            <div class="last2" style = 'background-image:url("pic/13.png")'>
                <button class="buttons" onclick="goToUrl('${url[12]}')">播放</button>
            </div>

            <div class="last2" style = 'background-image:url("pic/13.png")'>
                <button class="buttons" onclick="goToUrl('${url[13]}')">播放</button>
            </div>
        </div>`;
        $(".parent_win").append(a);
        blind()
}
// 跳转函数 
function goToUrl(url){
    // 当前页面跳转
    // window.location.href = url;
    // 如需 新标签页打开，替换上面这行为：
    window.open(url);
}

function search(){
    let txt = document.getElementById("search_input").value.trim();
    // console.log(txt);
    if (!txt) {
        return;
    }
    let url = 'https://cn.bing.com/search?q=' + encodeURIComponent(txt);
    console.log(url);
    goToUrl(url);
}
