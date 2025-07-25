# TODO: remove -n once meson-python & plugins depend on the same variantlib branch
BUILD = python -m build -nw
VARIANTS = v0 v1 v2 v3 v4 v5 v6

all: $(VARIANTS)

v0:
	$(BUILD)
	> $@

v1:
	$(BUILD) \
		-Cvariant-name='fictional_hw :: architecture :: hal9000' \
		-Cvariant-name='fictional_hw :: compute_accuracy :: 0' \
		-Cvariant-name='fictional_hw :: compute_capability :: 6' \
		-Cvariant-name='fictional_hw :: humor :: 2'
	> $@

v2:
	$(BUILD) \
		-Cvariant-name='fictional_hw :: architecture :: tars' \
		-Cvariant-name='fictional_hw :: compute_accuracy :: 8' \
		-Cvariant-name='fictional_hw :: compute_capability :: 8' \
		-Cvariant-name='fictional_hw :: humor :: 10'
	> $@

v3:
	$(BUILD) \
		-Cvariant-name='fictional_tech :: quantum :: foam' \
		-Cvariant-name='fictional_tech :: risk_exposure :: 1000000000' \
		-Cvariant-name='fictional_tech :: technology :: improb_drive'
	> $@

v4:
	$(BUILD) \
		-Cvariant-name='fictional_hw :: architecture :: deepthought' \
		-Cvariant-name='fictional_hw :: compute_accuracy :: 10' \
		-Cvariant-name='fictional_hw :: compute_capability :: 10' \
		-Cvariant-name='fictional_hw :: humor :: 0' \
		-Cvariant-name='fictional_tech :: quantum :: foam'
	> $@

v5:
	$(BUILD) \
		-Cvariant-name='fictional_tech :: quantum :: superposition' \
		-Cvariant-name='fictional_tech :: risk_exposure :: 25' \
		-Cvariant-name='fictional_tech :: technology :: auto_chef'
	> $@

v6:
	$(BUILD) \
		-Cvariant-name='fictional_hw :: architecture :: mother' \
		-Cvariant-name='fictional_hw :: compute_capability :: 4'
	> $@

clean:
	rm -f dist/*.whl $(VARIANTS)

.PHONY: all clean
