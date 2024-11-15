templateMainWin = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>600</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <property name="styleSheet">
   <string notr="true"/>
  </property>
  <widget class="QLabel" name="back">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>600</width>
     <height>400</height>
    </rect>
   </property>
  </widget>
  <widget class="QLabel" name="label_authorization">
   <property name="geometry">
    <rect>
     <x>220</x>
     <y>100</y>
     <width>121</width>
     <height>81</height>
    </rect>
   </property>
   <property name="font">
    <font>
     <family>Fixedsys</family>
     <pointsize>57</pointsize>
    </font>
   </property>
   <property name="text">
    <string>Авторизация</string>
   </property>
  </widget>
  <widget class="QLabel" name="label_image">
   <property name="geometry">
    <rect>
     <x>70</x>
     <y>0</y>
     <width>411</width>
     <height>150</height>
    </rect>
   </property>
  </widget>
  <widget class="QWidget" name="verticalLayoutWidget">
   <property name="geometry">
    <rect>
     <x>200</x>
     <y>170</y>
     <width>160</width>
     <height>169</height>
    </rect>
   </property>
   <layout class="QVBoxLayout" name="verticalLayout">
    <item>
     <widget class="QLabel" name="label_login">
      <property name="text">
       <string>Логин</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QLineEdit" name="loginline"/>
    </item>
    <item>
     <widget class="QLabel" name="label_password">
      <property name="text">
       <string>Пароль</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QLineEdit" name="passwordline"/>
    </item>
    <item>
     <widget class="QPushButton" name="entryBtn">
      <property name="text">
       <string>Войти</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QPushButton" name="registrationBtn">
      <property name="text">
       <string>Зарегистрироваться</string>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

templateRegWin = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>Form</class>
 <widget class="QWidget" name="Form">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>600</width>
    <height>400</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <property name="styleSheet">
   <string notr="true"/>
  </property>
  <widget class="QLabel" name="backg">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>600</width>
     <height>400</height>
    </rect>
   </property>
  </widget>
  <widget class="QLabel" name="label">
   <property name="geometry">
    <rect>
     <x>220</x>
     <y>100</y>
     <width>121</width>
     <height>81</height>
    </rect>
   </property>
   <property name="font">
    <font>
     <family>Fixedsys</family>
     <pointsize>57</pointsize>
    </font>
   </property>
   <property name="text">
    <string>Регистрация</string>
   </property>
  </widget>
  <widget class="QLabel" name="label_image">
   <property name="geometry">
    <rect>
     <x>70</x>
     <y>0</y>
     <width>411</width>
     <height>150</height>
    </rect>
   </property>
   <property name="text">
    <string/>
   </property>
   <property name="pixmap">
    <pixmap>../../../New Piskel.png</pixmap>
   </property>
  </widget>
  <widget class="QWidget" name="verticalLayoutWidget">
   <property name="geometry">
    <rect>
     <x>200</x>
     <y>170</y>
     <width>160</width>
     <height>169</height>
    </rect>
   </property>
   <layout class="QVBoxLayout" name="verticalLayout">
    <item>
     <widget class="QLabel" name="label_2">
      <property name="text">
       <string>Логин</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QLineEdit" name="login_line"/>
    </item>
    <item>
     <widget class="QLabel" name="label_3">
      <property name="text">
       <string>Пароль</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QLineEdit" name="password_line"/>
    </item>
    <item>
     <widget class="QPushButton" name="reg_btn">
      <property name="text">
       <string>Зарегистрироваться</string>
      </property>
     </widget>
    </item>
    <item>
     <widget class="QPushButton" name="backBtn">
      <property name="text">
       <string>Вернуться на главную</string>
      </property>
     </widget>
    </item>
   </layout>
  </widget>
 </widget>
 <resources/>
 <connections/>
</ui>
"""