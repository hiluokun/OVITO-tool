#Requires AutoHotkey v2.0

; ========== 配置部分 ==========
nextFileIndex := 76          ; 起始帧序号(对应frame001.csv等)
endFileIndex  := 150          ; 您想处理的最后帧序号(可改成10,20等)
waitTimeMs    := 20000      ; 等待时间(毫秒), 默认15秒, 让OVITO完成分析/刷新
saveFolder    := "E:\08Mg\Paper\Proposal20240824\dforMg_CT\Mgtensdis\"   ; 保存CSV文件的文件夹, 末尾带"\"并确保存在
useBOM        := false      ; 是否写入UTF-8 BOM (在某些Excel版本中有助于识别)
separator     := ","        ; 若Excel是英文环境,逗号通常可直接分列
                            ; 若欧洲语言环境,可改为 ";"

; 当按下鼠标中键(MButton)时, 自动执行批量处理
MButton::
{
    ; 声明这些变量是全局的:
    global nextFileIndex, endFileIndex, waitTimeMs, saveFolder, useBOM, separator
	i := nextFileIndex
    While (i <= endFileIndex)
    {
        ; 1) 全选 + 复制
        Send "^a"
        Sleep 200
        Send "^c"
        Sleep 300

        ; 2) 从剪贴板读取 & 替换 Tab->separator
        fileContents := A_Clipboard
        fileContents := StrReplace(fileContents, "`t", separator)

        ; 3) 如果要 BOM, 手动在文本开头加 0xEF 0xBB 0xBF
        if (useBOM)
        {
            bom := Chr(0xEF) . Chr(0xBB) . Chr(0xBF)
            fileContents := bom . fileContents
        }

        ; 4) 构造文件名 & 写入
        fileName := saveFolder . "frame" . Format("{:03}", i) . ".csv"
        FileAppend fileContents, fileName  ; 只用2个参数,避免"Too many parameters"

        ; 5) 提示音
        SoundBeep 1000, 200

        ; 6) 若尚未到最后一帧 => Alt+Right => 等待
        if (i < endFileIndex)
        {
            Send "!{Right}"   ; Alt+Right
            Sleep waitTimeMs
        }

        i++
    }

    nextFileIndex := endFileIndex + 1
    MsgBox "已自动处理完 " (endFileIndex - nextFileIndex + 1) " 帧数据."
}
