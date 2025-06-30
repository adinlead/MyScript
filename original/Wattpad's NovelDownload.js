// ==UserScript==
// @name         Wattpad's NovelDownload
// @namespace    http://tampermonkey.net/
// @version      V20250630.1
// @description  请自行翻阅小说致最后一页后，点击左侧
// @author       adinlead
// @match        https://www.wattpad.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=wattpad.com
// @grant        none
// ==/UserScript==
(function () {
    'use strict';

    let logger = {
        warn: function (msg) {
            alert(msg);
            console.warn(msg);
        }, info: function (msg) {
            console.info(msg);
        }
    };


    // 等待目标节点加载完成
    const waitForElement = (selector, callback) => {
        const element = document.querySelector(selector);
        console.log(element);
        if (element) {
            callback(element);
        } else {
            setTimeout(() => waitForElement(selector, callback), 500);
        }
    };
    // 从URL生成文件名的方法
    function getFilenameFromUrl() {
        // 获取不含查询参数的路径部分
        let path = decodeURIComponent(window.location.pathname);
        // 移除开头和结尾的斜杠
        const cleanPath = path.replace(/^\/|\/$/g, '');
        // 将剩余斜杠替换为减号
        return cleanPath.replace(/\//g, '-') || 'wattpad-story';
    }
    // 下载文本为文件的方法
    function downloadTextAsFile(text, filename) {
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.style.display = 'none';

        document.body.appendChild(a);
        a.click();

        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    // 获取小说内容
    function getStoryText() {
        let txt = '';

        // 1. 获取所有的pre节点
        const preNodes = document.querySelectorAll('pre');

        if (preNodes.length === 0) {
            logger.warn('未找到pre节点');
            return;
        }

        // 2. 遍历pre节点
        preNodes.forEach(pre => {
            // 3. 遍历pre节点中的所有p节点
            const pNodes = pre.querySelectorAll('p');

            pNodes.forEach(p => {
                // 创建p节点的副本
                const pClone = p.cloneNode(true);

                // 删除副本中的component-wrapper子节点
                const componentWrappers = pClone.querySelectorAll('.component-wrapper');
                componentWrappers.forEach(wrapper => wrapper.remove());

                // 获取处理后的文本
                const text = pClone.textContent.trim();

                // 4. 将文本拼接到变量txt后面（加换行）
                if (text) {
                    txt += text + '\n\n'; // 添加双换行提高可读性
                }
            });

            // 在每个pre节点内容后添加分隔线
            txt += '------------------------\n\n';
        });

        // 5. 输出结果
        console.log(txt);
        return txt;
    }

    // 目标节点选择器
    const targetSelector = "#sticky-nav > div.share-tools.vertical.hidden-xs.hidden-sm";
    // 等待目标节点加载完成后执行插入操作
    waitForElement(targetSelector, (targetElement) => {
        // 创建新的a元素
        const embedButton = document.createElement('a');
        embedButton.setAttribute('data-gtm-action', 'share:download');
        embedButton.className = 'share-download';
        embedButton.setAttribute('aria-hidden', 'true');
        embedButton.href = 'javascript:void(0)';
        embedButton.setAttribute('data-share-channel', 'embed');
        embedButton.style.backgroundColor = 'transparent';
        // 添加点击事件处理
        embedButton.addEventListener('click', function () {
            // 在这里编写点击按钮后要执行的代码
            logger.info('下载按钮被点击了');
            let storyText = getStoryText();
            if (storyText) {
                // 提示用户输入文件名
                const userInput = prompt('请输入文件名:', getFilenameFromUrl());

                // 处理用户输入
                let filename;
                if (userInput === null) {
                    // 用户点击了取消
                    logger.warn('下载失败：下载已取消');
                    return;
                } else if (userInput.trim() === '') {
                    // 用户输入为空，使用URL生成的文件名
                    filename = getFilenameFromUrl();
                } else {
                    // 使用用户输入的文件名，并添加txt扩展名
                    filename = userInput.trim();
                }

                // 确保文件名有扩展名
                if (!filename.endsWith('.txt')) {
                    filename += '.txt';
                }

                // 执行下载
                downloadTextAsFile(storyText, filename);
            } else {
                logger.warn('下载失败：未获取到文本内容');
            }
        });

        // 创建SVG元素
        const svgElement = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svgElement.setAttribute('t', '1751278616943');
        svgElement.setAttribute('class', 'icon');
        svgElement.setAttribute('viewBox', '0 0 1024 1024');
        svgElement.setAttribute('version', '1.1');
        svgElement.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
        svgElement.setAttribute('p-id', '11976');
        svgElement.setAttribute('width', '100%');
        svgElement.setAttribute('height', '100%');
        svgElement.style.display = 'block';
        svgElement.style.margin = 'auto';

        const pathElement = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        pathElement.setAttribute('d', 'M512 160c131.2 0 239.392 98.752 254.272 225.984a224 224 0 0 1-22.56 445.888L736 832H288a224 224 0 0 1-30.24-445.984A256 256 0 0 1 512 160z m64 293.504h-128v146.752h-78.4a16 16 0 0 0-11.296 27.296l131.072 131.072a32 32 0 0 0 45.248 0l131.072-131.072a16 16 0 0 0-11.296-27.328l-78.4 0.032v-146.752z');
        pathElement.setAttribute('fill', '#1296db');
        pathElement.setAttribute('p-id', '11977');

        svgElement.appendChild(pathElement);
        svgElement.setAttribute('aria-hidden', 'true');
        svgElement.style.fontSize = '24px';

        // 将SVG添加到a元素
        embedButton.appendChild(svgElement);

        // 将新元素插入到目标元素之后
        targetElement.appendChild(embedButton);
    });
})();

