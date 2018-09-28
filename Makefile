DESTDIR=/usr
NAME=
all:

install:
	mkdir ${DESTDIR}/lib/indicator-prayer-app
	cp src/* ${DESTDIR}/lib/indicator-prayer-app
	cp indicator-pprayer-app ${DESTDIR}/share/applications/
	
clean:
	rm -rf ../*.xz ../*.deb ../*.tar.gz ../*.changes ../*.dsc ../*.upload ../*.build ../*.cdbs-config_list
	
uninstall:
	rm -rf ${DESTDIR}/lib/indicator-sysmonitor
	rm ${DESTDIR}/bin/indicator-sysmonitor
	rm ${DESTDIR}/share/applications/indicator-sysmonitor.desktop

.PHONY: clean install all
