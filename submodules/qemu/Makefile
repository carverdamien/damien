all: image

image: chroot
chroot: debootstrap

%:%.sh
	sudo rm -rf $@
	bash $<

clean:
	sudo rm -rf chroot debootstrap

cleanall: clean
	sudo rm image
