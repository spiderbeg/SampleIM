
// 心跳包，定时请求数据
$(function(){
    self.setInterval("clock()", 2000);//数据请求间隔
});
// 记录当前聊天对象
localStorage.user = 'a'; 
// 请求当前最新消息状态，--主要逻辑
function clock() {
    $.getJSON('/imapi/total/', {}, function(data) {
        console.log('function: clock -> -> -> ->新的操作开始。。<- <- <- <- \n -> ->');
        // 从网页获取当前 登录用户名
        var sender = document.getElementById("username").innerHTML;
        // 修改用户列表，返回新登录用户列表
        var addusers = add_users(data,sender);
        
        //获取当前聊天对象节点
        var ac = $('#username_list>li.activate'); 
        //根据节点获取当前选择用户 id maxpk 属性，
        if (ac.length === 0){//当聊天用户退出时，自动返回群组聊天
            var resets = $('#username_list>li[id=first]'); 
            resets[0].setAttribute('class','activate');
            var ac = $('#username_list>li.activate');
        }
        var who = ac[0].getAttribute("id"); //当前聊天用户名 
        if (!ac[0].hasAttribute("maxpk")){// 还没有创建 maxpk 属性
            var maxid = 0;
        }else{
            var maxid = ac[0].getAttribute("maxpk"); // 当前对象最新 pk 值
        }
        console.log('function: clock -> 激活用户',who,'; 当前用户：',sender,'; 储存用户',localStorage.user);
        console.log('function: clock -> 消息状态',data);
        var tms = data.message_status; // 最新消息情况
        //生成当前用户键值
        if (who==='first'){
            var st = sender + '->' + 'firsttest';
        }else{
            var st = sender + '->' + who;
        }

        //当前聊天信息比较,
        // 1 当前用户登录第一次创建所有聊天信息 
        // 2 有用户登录创建基础的聊天信息，及用户列表的 maxpk minpk 属性 
        // 3 而后查看有无新消息
        var acs = $('#username_list>li'); //用户列表节点
        for (let i=0, len=acs.length; i<len; i++){
            var who2 = acs[i].getAttribute("id"); 
            if (who2===sender){
                continue;
            }
            //所有用户键值
            if (who2==='first'){
                var st2 = sender + '->' + 'firsttest';
            }else{
                var st2 = sender + '->' + who2;
            }
            if (maxid === 0 && who === 'first'){//当前用户初次登录 获取所有最近消息
                if (who2==='first'){
                    gethistory(who2,acs[i],data.message_status,style=0);
                }else{
                    gethistory(who2,acs[i],data.message_status,style=1);
                }
                //添加消息记录操作
                var user2 =  document.getElementById(who2);
                //设定最大值 pk; minpk 会在 gethistory 中设置
                user2.setAttribute("maxpk", tms[st2]);
            }else if(addusers.length != 0 && addusers.includes(who2)){// 新用户登录时 
                console.log('function: clock -> 新用户登录呢',addusers)
                gethistory(who2,acs[i],data.message_status,style=1);
                
                //添加消息记录操作
                var user2 =  document.getElementById(who2);
                //设定最大值 pk; minpk 会在 gethistory 中设置
                user2.setAttribute("maxpk", tms[st2]);
            }else{//非第一次请求，有新信息改变颜色
                var maxpk2 = acs[i].getAttribute("maxpk"); 
                var status = acs[i].children[1].children[1].children[0]; // 定位到 span 节点
                if(maxpk2<tms[st2] && who2 != who){ // 保证自己发的时候不会变色
                    status.setAttribute("class", "status orange");
                }else{
                    status.setAttribute("class", "status green");
                }
            }
        }

        //判断操作

        if(localStorage.user != who){ // 1 切换回
            console.log('function: clock -> 显示该用户聊天信息',who);
            //修改当前聊天用户
            change_talker(who);
            //聊天页面自动滚动到最底部
            var d=$("#chat");
            d[0].scrollTop = d[0].scrollHeight;
        }
        if(maxid != tms[st] && maxid != 0){// 2 更新最新消息
            //更新最新消息, maxpk 会在 get_newest() 内添加
            get_newest(sender,ac[0]);//滚动到底部在函数内实现
        }else{
            console.log('function: clock -> 无新消息');
        }
        localStorage.user = who;//记录当前聊天对象

    })//getjson
}//clock()

//实现的函数

//改变聊天对象, 使当前显示对象显示出来
function change_talker(who){
    var li = $('#chat>li'); //获取节点
    for(var i=0, len=li.length; i<len;i++){
        if(li[i].getAttribute("name")===who){
            li[i].removeAttribute('style');
        }else{
            li[i].setAttribute('style','display:none;');
        }
    }
}

//这是比较函数，用户私聊按 pk 升序排列
function compare(p){ 
    return function(m,n){
        var a = m[p];
        var b = n[p];
        return a - b; //升序
    }
}

//添加管理用户列表
function add_users(data,sender){
    // 输入：用户列表信息，当前用户名
    // 输出：添加的用户列表
    //获取前端用户列表
    var li3 = $('#user_list>ul>li');
    var ulist = [];
    for(let i=0, len=li3.length; i<len; i++){
        let liid = li3[i].getAttribute("id");
        ulist.push(liid);
    }
    console.log('function:add_user -> ulist',ulist); // 用户列表
    // 接收后端返回用户列表
    var us = data.users;
    var ulist2 = ['first'];
    for (var i=0, len=us.length; i<len; i++){
        ulist2.push(us[i].username);
    }
    console.log('function:add_user -> ulist2',ulist2);
     // 1 li3 前端用户列表节点 删除退出用户
    for(let i=0, len=li3.length; i<len; i++){
        let liid = li3[i].getAttribute("id");
        if(!ulist2.includes(liid)){
            var sel = '#chat>li[name='+ liid +']';
            li3[i].remove();//删除用户列表元素
            //删除聊天列表相关内容
            var userchat = $(sel);
            userchat.remove();
        }
    }
    //记录添加的用户
    var addusers = [];
    // 用户有无消息指示灯
    var sh = '</h2> <h3> <span class="status green"></span> online </h3> </div> </li>';
    // 用户列表节点
    var chat2 = $('#user_list>ul');
    // 添加群组
    if(!ulist.includes('first')){
        var sb = '<li id="first" class="activate"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
        chat2.append(sb + 'first' + sh);
    }
    // ulist2 后端返回用户列表，添加新用户
    for (var i=0, len=us.length; i<len; i++){//隐藏用户自己的名字
        if(!ulist.includes(us[i].username)){
            if(us[i].username != sender){
                addusers.push(us[i].username)//记录新登录的用户
                var sb = '<li id="' + us[i].username + '"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
            }else{
                var sb = '<li style="display: none;" id="' + us[i].username + '"> <img src="https://s3-us-west-2.amazonaws.com/s.cdpn.io/1940306/chat_avatar_01.jpg" alt="avatar"> <div>  <h2>';
            }
            var sq = sb + us[i].username + sh;
            chat2.append(sq);
        } 
    };
    return addusers;
}

// 发送群消息
// 1 获取 cookie 
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
// 2.1 发送群消息 私聊消息
function post_message(url=null,type='T'){
    // 信息预备，发送者及接收者
    // 发送方 获取用户名
    var sender = document.getElementById("username").innerHTML; // 获取网页内容
    // 接收方
    var ac = $('#username_list>li.activate'); //激活用户
    if(!ac[0].hasAttribute("id")){
        console.log("function：post_message -> 暂无激活用户");
        return false;
    }
    var who = ac[0].getAttribute("id"); // 获取当前选择用户
    // csrftoken
    var csrftoken = getCookie('csrftoken'); // csrf
    console.log('function：post_message ->  信息类型: ', type)
    if (type==='T'){
        var messageinput = document.getElementById("inpumessage");
        var message = messageinput.value; //获取输入框内容
    }else if(type==='P'){
        var message = url;
    }else if(type='I'){
        var message = url;
    }else{
        console.log('没有反应！？？！？')
        return
    }
    
    console.log(sender, message)
    if(who==='first'){
        var surl = '/imapi/groupmessage/';
        var sdata = {'message':message,'sender':sender, 'mtype':type};
    }else{
        var surl = '/imapi/usermessage/';
        var sdata = {'message':message,'sender':sender,'to':who,'mtype':type};
    }
    $.ajax({
        type: "POST",
        url: surl,
        data: sdata,
        headers:{"X-CSRFToken": csrftoken},
        success: function (newEnd) {
            console.log(newEnd);
        },
        error: function () {
            alert("There was an error, please try again!");
        }
    });
    if(url===null){
        messageinput.value = "" //清空输入框
    }
}   


//获取历史消息 
// 1 比较函数 用户 pk 值降序排列
function compare2(p){ //这是比较函数
    return function(m,n){
        var a = m[p];
        var b = n[p];
        return b - a; //降序
    }
}
// 2 请求发送
function gethistory(who=null,li=null,data=1,style=2){
    // 数据准备
    //获取当前用户名
    var sender = document.getElementById("username").innerHTML; // 获取网页内容
    //获取聊天对象
    if (who===null | li === null){//无参数输入时, 正常获取历史消息
        //获取聊天对象
        var lis = $('#username_list>li.activate'); //激活用户
        if(lis[0]!=null){//第一次获取不到，所以忽略第一次
            var who = lis[0].getAttribute("id"); // 获取当前选择用户
            var li = lis[0] //当前选中节点
        }else{
            return
        }
    }
    //激活用户 节点 li
    var who = li.getAttribute("id"); // 获取当前选择用户

    if(who==='first'){
        var type = 'group';
    }else{
        var type = 'personal'
    };
    if (li.hasAttribute("minpk")){
        var minpk = li.getAttribute("minpk");
    }else{
        if (type=='group'){
            var s = sender + '->' + 'firsttest';
        }else{
            var s = sender + '->' + who;
        }
        var minpk = data[s] + 1;
        console.log('function:gethistory -> 首次获取历史记录，应该在最新记录上加 1',data[s]);
    }
    console.log('function:gethistory -> 历史记录传输消息',sender,who,type,minpk);
    //发送请求
    $.getJSON('/imapi/historymessage/', {"user1":sender,"user2":who,"type":type,"minpk":minpk}, function(history){
        // 加载历史消息
        handle_history(history, type,sender,who,li,style);
    });

}
// 第二步的历史数据处理三种情况 1 首次登录 first 显示 2 首次登录其他用户 不显示 3 获取其他用户信息显示
function handle_history(history, type, sender,who,li,style){
    console.log('function:handle_history -> 历史消息',history);
    if (type === 'personal'){
        // 接收用户信息预备 1
        var uml2 = [];
        var um = history;
        var s1 = who + ' -> ' + sender;
        var s2 = sender + ' -> ' + who;
        console.log('function:handle_history -> ', s1, s2, um[s1], um[s2]);
        if(um[s1] != undefined){
            for(var i=0, len=um[s1].length; i<len; i++){
                uml2.push(um[s1][i]);
            }
        }
        if(um[s2] != undefined){
            for(var i=0, len=um[s2].length; i<len; i++){
                uml2.push(um[s2][i]);
            }
        }
        uml2.sort(compare2("pk"));
        console.log('function:handle_history -> 用户信息',uml2);
        if(uml2.length === 0){
            return false;
        }
        var history = uml2;
    }else if(history.length===0){//已无用户群聊信息，退出
        return false;
    }
    //处理数据
    //加载历史记录
    if (style===0){//用户登录第一次 显示群组信息使用
        history.reverse() 
    }
    
    chat = $("#main>ul"); //聊天内容
    for(var i=0, len=history.length; i<len; i++){
        var i2 = i;

        if (type==='group'){
            var sendtime = '<h3>'+ history[i2].timeg.substring(0,19) +'</h3>';
        }else{
            var sendtime = '<h3>'+ history[i2].timeu.substring(0,19) +'</h3>';
        }
        
        var senduser = ' <h2>' + history[i2].sender + '</h2>';
        if (history[i2].mtype ==='T'){//文字消息
            var sendmessage = '<div class="message">' + escapeHtml(history[i2].message) + '</div>';
        }else if (history[i2].mtype ==='P'){//图片消息    
            var sendmessage = '<div class="message"> <img src='+ history[i2].message +' class="displaypicture"></div>';
        }else if(history[i2].mtype ==='I'){
            var sendmessage = '<div class="message"> <img src='+ history[i2].message +' class="displayemoji"></div>';
        }

        if(history[i2].sender===sender){
            var s = '<li  name=' + who +' class="me"> <div class="entete"> <span class="status blue"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
        }else{
            var s = '<li  name=' + who +' class="you"> <div class="entete"> <span class="status green"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
        }
        if(history[i2].sender===sender){
            var s2 = '<li style="display: none;" name=' + who +' class="me"> <div class="entete"> <span class="status blue"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
        }else{
            var s2 = '<li style="display: none;" name=' + who +' class="you"> <div class="entete"> <span class="status green"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>'
        }

        if (style===0){
            chat.append(s);
        }else if(style===1){
            // 添加内容，这是 jquery 写法 https://www.w3school.com.cn/jquery/jquery_dom_add.asp
            //另外还有 DOM 的写法 -搜索-js 修改节点
            $('#history').after(s2);
        }else{
            $('#history').after(s);
        }
    }
    if (style===0){
        console.log('function:handle_history -> 第一次的登录 & 设置 minpk',history[0].pk,history[history.length-1].pk);
        li.setAttribute("minpk", history[0].pk);//记录最小  pK
        // 文本下拉
        var d=$("#chat");
        d[0].scrollTop = d[0].scrollHeight;
    }else{
        console.log('function:handle_history -> 历史消息序号 & 设置 minpk',history[0].pk,history[history.length-1].pk);
        li.setAttribute("minpk", history[history.length-1].pk);//记录最小  pK
    }
}

// 添加最新消息
function get_newest(sender,ac){
    // 数据准备 当前登录用户、当前聊天对象节点、第一次的判断条件
    var who = ac.getAttribute("id"); // 获取当前选择用户
    if(who==='first'){
        var type = 'group';
    }else{
        var type = 'personal';
    };
    var maxpk = ac.getAttribute("maxpk");
    console.log('function: get_newest -> maxpx',sender,who,type,maxpk);
    //发送请求
    $.getJSON('/imapi/newestmessage/', {"user1":sender,"user2":who,"type":type,"maxpk":maxpk}, function(newest){
        // 加载最新消息
        console.log('function: get_newest -> 最新',newest);
        handle_newest(newest,type,sender,who,ac);
        //聊天页面自动滚动到最底部
        var d=$("#chat");
        d[0].scrollTop = d[0].scrollHeight;
    });
}
// 添加最新消息
function handle_newest(newest,type,sender,who,ac){
    //用户消息处理
    // 1 整理用户最新消息
    if (type === 'personal'){
        // 接收用户信息预备 1
        var uml2 = [];
        var um = newest;
        var s1 = who + ' -> ' + sender;
        var s2 = sender + ' -> ' + who;
        console.log('function:handle_newest -> 预备数据 ',s1, s2, um[s1], um[s2]);
        if(um[s1] != undefined){
            for(var i=0, len=um[s1].length; i<len; i++){
                uml2.push(um[s1][i]);
            }
        }
        if(um[s2] != undefined){
            for(var i=0, len=um[s2].length; i<len; i++){
                uml2.push(um[s2][i]);
            }
        }
        uml2.sort(compare("pk"));
        console.log('function:handle_newest -> 用户信息',uml2);
        if(uml2.length === 0){
            return false;
        }
        var newest = uml2;
    }else if(newest.length===0){//已无用户群聊信息，退出
        return false;
    }
    // 2 添加最新消息
    chat = $("#main>ul"); //聊天内容
    console.log(chat)
    for(var i=0, len=newest.length; i<len; i++){
        var i2 = i;
        if (type==='group'){
            var sendtime = '<h3>'+ newest[i2].timeg.substring(0,19) +'</h3>';
        }else{
            var sendtime = '<h3>'+ newest[i2].timeu.substring(0,19) +'</h3>';
        }
        
        var senduser = ' <h2>' + newest[i2].sender + '</h2>';
        console.log('function:handle_newest -> mtype: ', newest[i2].mtype)
        if (newest[i2].mtype ==='T'){//文字消息
            var sendmessage = '<div class="message">' + escapeHtml(newest[i2].message) + '</div>';
        }else if (newest[i2].mtype ==='P'){//图片消息
            var sendmessage = '<div class="message"> <img src='+ newest[i2].message +' class="displaypicture"></div>';
        }else if(newest[i2].mtype ==='I'){
            var sendmessage = '<div class="message"> <img src='+ newest[i2].message +' class="displayemoji"></div>';
        }
        if(newest[i2].sender===sender){
            var s = '<li name= '+ who +' class="me"> <div class="entete"> <span class="status blue"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>';
        }else{
            var s = '<li name= '+ who +' class="you"> <div class="entete"> <span class="status green"></span>' + senduser + sendtime + '</div> <div class="triangle"></div>' + sendmessage + '</li>';
        }

        chat.append(s);
    };
    ac.setAttribute("maxpk", newest[newest.length-1].pk);//记录最大  pK
}

//点击改变聊天对象颜色
$(document).ready(function(){// jquery 写法，页面加载完毕后执行
    document.getElementById("username_list").addEventListener("click", someFunction);
});
function someFunction(event) {
    var user =  document.getElementById(event.target.id);
    if(user != null && event.target.id != "username_list"){ //确保只点击用户
        var li3 = $('#user_list>ul>li');
        for(var i=0, len=li3.length; i<len; i++){
            li3[i].setAttribute("class", "deactivate");
        }
        user.setAttribute("class", "activate");
        }
}
// html 标签转移函数
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// 利用 formdata 发送处理好的到远程服务器，并返回 url
$(document).ready(function(){
    console.log('function: 文件选择监听')
    //表单
    var fileInput = document.getElementById('fileinput');
    // 监听change事件:
    fileInput.addEventListener('change', function () {
        // 获取File引用:
        var file = fileInput.files[0];
        if (file.type !== 'image/jpeg' && file.type !== 'image/png' && file.type !== 'image/gif') {
            alert('不是有效的图片文件!');
            return;
        }
        // formdata: 将文件以模仿表单的形式提交
        var formData = new FormData();
        formData.append("fileInput", file);
        post_image(formData,file.name);
    });
})  
// 上传图片，返回图片链接
function post_image(data,filename="file"){
    console.log('function: post_image -> 发送图片');
    // csrftoken
    var csrftoken = getCookie('csrftoken'); // csrf
    $.ajax({
        type: "POST",
        url: '/imapi/imagefile/',
        data: data,
        contentType:"multipart/form-data", 
        processData: false, // jQuery不要去处理发送的数据
        contentType: false, // jQuery不要去设置Content-Type请求头
        headers:{"X-CSRFToken": csrftoken, "Content-Disposition":'attachment; filename=' + filename,},
        success: function (image_url) {
            console.log('function:post_image -> 返回的图片地址',image_url['image_path']);
            // 发送图片消息
            post_message(url=image_url['image_path'],type='P'); 
            console.log('function: post_image -> 发送图片消息');
            // 清空文件输入
            document.querySelector('#fileinput').value = ''; 
        },
        error: function () {
            alert("There was an error, please try again!");
        }
    });
}

// 显示 emoji 图像
function emoji(){
    // 按钮
    var button = document.getElementById('emojibutton');
    var text = document.getElementById("inpumessage");
    if(!text.hasAttribute("style")){
        text.setAttribute("style","display:none;");
        button.innerHTML = 'Return';
    }else{
        text.removeAttribute("style");
        button.innerHTML = 'Emoji';
    }
    var em = document.getElementById("emoji");
    if(em.hasAttribute("style")){
        em.removeAttribute("style");
    }else{
        em.setAttribute("style","display:none;");
    }
    console.log('function:emoji -> 显示 emoji')
}
//选择 emoji 并发送
function check_emoji(e){
    var emoji_url = e.children[0].getAttribute("src");
    console.log('function: check_emoji -> 发送的 emoji 地址 ',emoji_url);
    // 发送信息
    post_message(url=emoji_url, type='I');
    // 隐藏 emoji
    emoji();
}

//选择图片
function related_image() {
    $("#fileinput").click()
}

// 测试用--django 表单图片传送测试
function test(){
    console.log('function: django 表单图片传送测试');
    //表单
    var formData = new FormData();
    var filei = document.getElementById('err2');
    formData.append("fileInput", filei.files[0]);
    post_image(formData);
        
}
// //检测页面关闭, 暂时不考虑
// window.addEventListener("beforeunload", function (e) {
//     $.getJSON('/imapi/groupmgpk/', {}, function(history){
//         console.log('are you ok ', history)
//     })
//     console.log('llllllllllllllllllllllll');
//     var confirmationMessage = "\o/";
//     (e || window.event).returnValue = confirmationMessage; //Gecko + IE
//     return confirmationMessage;                            //Webkit, Safari, Chrome
//   });


