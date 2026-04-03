from jnius import autoclass, PythonJavaClass, java_method
from plyer import gps

# Android classes
Context = autoclass('android.content.Context')
NotificationBuilder = autoclass('android.app.Notification$Builder')
NotificationManager = autoclass('android.app.NotificationManager')
PendingIntent = autoclass('android.app.PendingIntent')
Intent = autoclass('android.content.Intent')
PythonService = autoclass('org.kivy.android.PythonService')

class GPSListener(PythonJavaClass):
    __javainterfaces__ = ['android/location/LocationListener']
    __javacontext__ = 'app'

    @java_method('(Landroid/location/Location;)V')
    def onLocationChanged(self, location):
        lat = location.getLatitude()
        lon = location.getLongitude()
        print(f"SERVICE_GPS {lat} {lon}")

    @java_method('(Ljava/lang/String;)V')
    def onProviderDisabled(self, provider):
        pass

    @java_method('(Ljava/lang/String;)V')
    def onProviderEnabled(self, provider):
        pass

    @java_method('(Ljava/lang/String;I[Landroid/os/Bundle;)V')
    def onStatusChanged(self, provider, status, extras):
        pass


def start_service():
    service = PythonService.mService

    # Notification (obbligatoria per Android 8+)
    notification = NotificationBuilder(service)
    notification.setContentTitle("Running App")
    notification.setContentText("GPS attivo in background")
    notification.setSmallIcon(service.getApplicationInfo().icon)
    service.startForeground(1, notification.build())

    # Start GPS
    gps.configure(on_location=lambda **kwargs: None)
    gps.start(minTime=1000, minDistance=1)


if __name__ == '__main__':
    start_service()
