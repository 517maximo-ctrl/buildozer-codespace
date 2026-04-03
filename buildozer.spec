[app]
title = Running App by Massimo Moretti
package.name = runningappfp
package.domain = it.massimomoretti.app
version = 1.0
source.dir = .
source.include_exts = py,kv,png,jpg,json
source.include_patterns = Tbl_Program_Training.json
icon.filename = Images/AppRunner.png
presplash.filename = Images/AppRunner.png
requirements = python3,kivy,pillow
orientation = portrait
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.use_legacy_storage = True
android.allow_backup = True
android.api = 34
android.compile_sdk = 34
android.target_sdk = 34
android.archs = arm64-v8a
p4a.branch = master
android.bootstrap = sdl2
android.enable_androidx = True
android.enable_jetifier = True
android.gradle_dependencies = androidx.core:core:1.9.0, androidx.appcompat:appcompat:1.6.1
android.manifest_placeholders = file_provider_authority=it.massimomoretti.app.runningappfp.fileprovider
android.add_res_xml = res/xml/filepaths.xml
android.add_manifest_xml = <provider android:name="androidx.core.content.FileProvider" android:authorities="${file_provider_authority}" android:exported="false" android:grantUriPermissions="true"><meta-data android:name="android.support.FILE_PROVIDER_PATHS" android:resource="@xml/filepaths"/></provider>

