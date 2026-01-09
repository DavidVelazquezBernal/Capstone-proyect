<template>
    <v-container v-if="oneRowTable" data-cy="table_oneRow" :class="['pop2-table oneRowTable', values && values.length === 0 && 'no-data']">
        <!-- One Row Table -->
        <v-row v-if="values && values.length === 0">
            <v-col class="text-center text-body-2">
                {{ $t("app.noDataAvailable") }}
            </v-col>
        </v-row>
        <v-row v-else @mouseover="setFunctionMouseOver2(0)" @mouseleave="setFunctionMouseLeave2">
            <v-col :cols="12" :sm="getNumColumns(header)" v-for="(header, i) in headersWithoutHiddenHeaders" :key="i">
                <div v-if="allowHeader" class="header text-body-2 font-weight-medium">
                    {{ showHeaderText(header) }}
                </div>
                <div class="cell text-body-2">
                    <component
                        :is="header.type"
                        :id="trimStringToBeValidId(header.name) + '_' + header.id"
                        v-bind="{
                            ...header.props,
                            disabled: isDisabled(header, 0) || GetDisabledRegister(disableRegister, disableRegisterItemId, 0)
                        }"
                        :is-in-edit-mode="isInEditMode"
                        :record-index="nLevelBodyTable ? recordIndex : 0"
                        :record-index-from-other-section="nLevelBodyTable ? recordIndex : 0"
                        :value="getValueOneRow(header)"
                        :record-id="getRecordId(values[nLevelBodyTable ? recordIndex : 0])"
                        :record-state="getRecordState(values[nLevelBodyTable ? recordIndex : 0])"
                        no-label
                        is-in-table
                        :any-mandatory-component-is-empty="anyMandatoryComponentIsEmpty"
                        :section="header.type === 'pop2-section' ? header : null"
                        :gallery="header.type === 'pop2-gallery' ? header : null"
                        :group="header.type === 'pop2-group' ? header : null"
                        :radiobuttongroup="header.type === 'pop2-radiobuttongroup' ? header : null"
                        :dynamicfilter="header.type === 'pop2-dynamicfilter' ? header : null"
                        :actions="header.type === 'pop2-kebabmenu' ? header.actions : null"
                        :itemDataToShow="header.type === 'pop2-label' && header.props.itemDataToShow === 'both' ? 'value' : header.props.itemDataToShow"
                        :screenUUID="screenUUID"
                        :component-name="header.name"
                        :component-type="header.type"
                        :component-id="header.id"
                        :section-name="sectionName"
                        @exec-method="execMethod"
                        @exec-code="execCode"
                        @exec-hyperlink="execHyperlink"
                        @exec-pop2-message="execPop2Message"
                        @check-mandatory="checkMandatory"
                        @exec-action="execAction"
                        @check-is-in-edit-mode-section="checkIsInEditModeSection"
                    />
                </div>
            </v-col>
        </v-row>
    </v-container>

    <v-data-table
        v-else
        v-model="selected"
        v-model:expanded="expanded"
        @update:modelValue="selectAllItems"
        :headers="headersWithOutTextArea"
        :items="values"
        v-model:items-per-page.sync="itemsPerPage"
        :items-per-page-options="itemsPerPageOptions"
        :page-text="getFooterString()"
        v-model:page.sync="page"
        :class="[
            'pop2-table',
            isSmAndDown && 'table-mobile',
            isInEditMode && 'table-isInEditMode',
            getAllowSelect && 'table-isSelectable',
            tableLayoutFixed && 'table-layout-fixed',
            tableAllBorders && 'table-all-borders',
            values && values.length === 0 && 'no-data'
        ]"
        :show-expand="headersOnlyWithTextArea.length > 0"
        item-key="index"
        mobile-breakpoint="960"
        :show-select="getAllowSelect"
        return-object
        :density="tableDense ? 'compact' : 'comfortable'"
        @update:options="updatePagination($event)"
        component="pop2-table"
        data-cy="table_multiRow"
    >
        <!-- APAÑO TEMPORAL HASTA QUE NO PONGAN LAS PROPIEDADES EN LA TABLA -->
        <template #bottom v-if="hideFooter"></template>

        <!-- Headers -->
        <template v-if="!hideHeader && !isSmAndDown" v-slot:headers="{ columns, getSortIcon, isSorted, toggleSort }">
            <tr>
                <th
                    v-for="column in columns"
                    :key="column.key"
                    :id="column.id"
                    colspan="1"
                    rowspan="1"
                    :width="column.width"
                    :class="[
                        'v-data-table__td',
                        'v-data-table-column--align-start',
                        { 'v-data-table__th--sortable': column.sortable },
                        { 'v-data-table__th--sorted': isSorted(column) },
                        'v-data-table__th'
                    ]"
                >
                    <div class="v-data-table-header__content" @click="toggleSort(column)" :data-cy="'pop2-table_column_' + column.title">
                        <span @click="toggleSort(column)" v-text="column.title" :data-cy="'pop2-table_column_label_' + column.title"></span>
                        <span v-if="column.mandatory" class="mandatory-asterisk" :data-cy="'pop2-table_column_label_asterisk_' + column.title">*</span>
                        <v-icon
                            v-if="column.sortable"
                            :icon="getSortIcon(column)"
                            class="v-data-table-header__sort-icon"
                            :data-cy="'pop2-table_column_sortIcon_' + column.title"
                            aria-hidden="true"
                        ></v-icon>
                    </div>
                </th>
            </tr>
        </template>
        <template #headers v-else-if="hideHeader || isSmAndDown"></template>

        <!-- Allow add register -->
        <template v-if="allowAddRegister" v-slot:top>
            <div class="d-flex mb-4">
                <v-btn :disabled="checkDisabled(disabled, entityId, path, itemId, recordIndex)" prepend-icon="mdi-plus" variant="text" color="primary" @click="clickAddRegister()">
                    {{ $t("section.addRegister") }}
                </v-btn>
            </div>
        </template>

        <!-- Mobile mode -->
        <template v-if="isSmAndDown" v-slot:item="{ internalItem, item }">
            <div :class="['table-mobile d-flex align-center tr-table', selectedItemId && isSelectedItem(internalItem) && 'row-selected', item.index !== values.length - 1 && 'border-bottom']">
                <div v-show="getAllowSelect" class="pa-4 select-check-box" data-cy="checkboxSelectedElementMobile">
                    <v-checkbox
                        :aria-label="vueInstance().$t('a11y.selectRegister')"
                        :model-value="isSelectedItem(internalItem)"
                        @update:modelValue="selectItem($event, internalItem)"
                        density="comfortable"
                        hide-details="auto"
                    />
                </div>

                <v-card class="flex-grow-1 card-container" variant="outlined" elevation="1">
                    <v-card-text class="mb-0 py-0">
                        <div
                            v-for="(header, i) in headersWithoutHiddenHeaders"
                            :class="[header.type === 'pop2-timer' ? 'd-none' : 'v-data-table__mobile-row pa-0 flex-column align-start']"
                            :key="i"
                            @click.stop="clickRow(internalItem, !isSelectedItem(internalItem))"
                        >
                            <div
                                v-if="allowHeader && !isInEditMode && checkVisibilitForComponent(header, item.index)"
                                class="v-data-table__mobile-row__header px-1 pt-2 pb-0 text-body-2 font-weight-medium"
                            >
                                {{ header.title }}
                            </div>

                            <div :class="['v-data-table__mobile-row__cell px-1 py-2 width-100 text-left overflow-hidden position-relative z-index-1', !isInEditMode && 'text-body-2']">
                                <div v-if="header.key === 'actions'">
                                    <v-btn
                                        icon="mdi-delete"
                                        variant="outlined"
                                        density="comfortable"
                                        :block="true"
                                        :disabled="
                                            isDisabled(header, item.index) ||
                                            getRecordState(internalItem) === 'Deleted' ||
                                            GetDisabledRegister(disableRegister, disableRegisterItemId, item.index) ||
                                            GetDisabledAllowRemoveRegister(allowRemoveRegister, allowRemoveRegisterItemId, item.index)
                                        "
                                        @click="clickRemoveRegister(item.index)"
                                        :aria-label="$t('a11y.deleteRegister')"
                                    />
                                </div>

                                <component
                                    v-else
                                    :is="header.type"
                                    :id="trimStringToBeValidId(header.name) + '_' + header.id"
                                    v-bind="{
                                        ...header.props,
                                        disabled: isDisabled(header, item.index) || GetDisabledRegister(disableRegister, disableRegisterItemId, item.index)
                                    }"
                                    :is-in-edit-mode="isInEditMode"
                                    :record-index="item.index"
                                    :record-index-from-other-section="item.index"
                                    :section="header.type === 'pop2-section' ? header : null"
                                    :gallery="header.type === 'pop2-gallery' ? header : null"
                                    :group="header.type === 'pop2-group' ? header : null"
                                    :radiobuttongroup="header.type === 'pop2-radiobuttongroup' ? header : null"
                                    :dynamicfilter="header.type === 'pop2-dynamicfilter' ? header : null"
                                    :actions="header.type === 'pop2-kebabmenu' ? header.actions : null"
                                    :value="header.type !== 'pop2-datepickerinput' ? item[header.key] : null"
                                    :record-id="getRecordId(internalItem)"
                                    :record-state="getRecordState(internalItem)"
                                    :any-mandatory-component-is-empty="anyMandatoryComponentIsEmpty"
                                    :screenUUID="screenUUID"
                                    :component-name="header.name"
                                    :component-type="header.type"
                                    :component-id="header.id"
                                    :section-name="sectionName"
                                    is-in-table
                                    @exec-method="execMethod"
                                    @exec-code="execCode"
                                    @exec-hyperlink="execHyperlink"
                                    @exec-pop2-message="execPop2Message"
                                    @check-mandatory="checkMandatory"
                                    @exec-action="execAction"
                                    @check-is-in-edit-mode-section="checkIsInEditModeSection"
                                />
                            </div>
                        </div>
                    </v-card-text>
                </v-card>
            </div>
        </template>

        <!-- View edit and read mode -->
        <template v-else v-slot:item="{ internalItem, toggleExpand, isExpanded, item }">
            <tr
                @mouseover="setFunctionMouseOver2(item.index)"
                @mouseleave="setFunctionMouseLeave2"
                :class="['tr-table', selectedItemId && isSelectedItem(internalItem) && 'row-selected', 'edit-read']"
            >
                <td v-if="getAllowSelect" style="width: 1px; min-width: 1px" class="select-check-box py-2 px-4" data-cy="checkboxSelectedElement">
                    <v-checkbox
                        :aria-label="vueInstance().$t('a11y.selectRegister')"
                        :model-value="isSelectedItem(internalItem)"
                        :disabled="GetDisabledRegister(disableRegister, disableRegisterItemId, item.index)"
                        @update:modelValue="selectItem($event, internalItem)"
                        density="comfortable"
                        hide-details="auto"
                    />
                </td>

                <td
                    v-for="(header, i) in headersWithOutTextArea"
                    :style="'width:' + header.width + '; min-width: ' + header.width + '; max-width: ' + header.width"
                    header.key
                    :class="[!tableDense && 'py-2 px-4', getCellClass(header, item.index)]"
                    :key="i"
                    @click.stop="clickRow(internalItem, !isSelectedItem(internalItem))"
                >
                    <div v-if="header.key === 'data-table-expand'">
                        <v-btn
                            v-if="checkVisibilityForRecord(headersOnlyWithTextArea, item.index)"
                            icon="mdi-chevron-down"
                            variant="text"
                            density="comfortable"
                            :class="['expandIcon', isExpanded(internalItem) ? 'expanded' : '']"
                            @click.stop="toggleExpand(internalItem)"
                            data-cy="tableBtnExpand"
                            :aria-label="isExpanded(internalItem) ? $t('a11y.collapse', [$t('a11y.register')]) : $t('a11y.expand', [$t('a11y.register')])"
                        />
                    </div>
                    <div v-else-if="header.key === 'actions'">
                        <v-btn
                            :disabled="
                                isDisabled(header, item.index) ||
                                getRecordState(item) === 'Deleted' ||
                                GetDisabledRegister(disableRegister, disableRegisterItemId, item.index) ||
                                GetDisabledAllowRemoveRegister(allowRemoveRegister, allowRemoveRegisterItemId, item.index)
                            "
                            icon="mdi-delete"
                            variant="text"
                            density="comfortable"
                            @click="clickRemoveRegister(item.index)"
                            :aria-label="$t('a11y.deleteRegister')"
                        />
                    </div>

                    <component
                        v-else-if="header.type !== 'pop2-textarea'"
                        :is="header.type"
                        :id="trimStringToBeValidId(header.name) + '_' + header.id"
                        :section="header.type === 'pop2-section' ? header : null"
                        :gallery="header.type === 'pop2-gallery' ? header : null"
                        :group="header.type === 'pop2-group' ? header : null"
                        :radiobuttongroup="header.type === 'pop2-radiobuttongroup' ? header : null"
                        :dynamicfilter="header.type === 'pop2-dynamicfilter' ? header : null"
                        :is-in-edit-mode="isInEditMode"
                        :record-index="item.index"
                        :no-label="allowHeader"
                        is-in-table
                        :record-index-from-other-section="item.index"
                        :value="header.type !== 'pop2-datepickerinput' ? item[header.key] : null"
                        :record-id="getRecordId(item)"
                        :record-state="getRecordState(item)"
                        :actions="header.type === 'pop2-kebabmenu' ? header.actions : null"
                        v-bind="{
                            ...header.props,
                            disabled: isDisabled(header, item.index) || GetDisabledRegister(disableRegister, disableRegisterItemId, item.index)
                        }"
                        :any-mandatory-component-is-empty="anyMandatoryComponentIsEmpty"
                        :screenUUID="screenUUID"
                        :component-name="header.name"
                        :component-type="header.type"
                        :component-id="header.id"
                        :section-name="sectionName"
                        @exec-method="execMethod"
                        @exec-code="execCode"
                        @exec-hyperlink="execHyperlink"
                        @exec-pop2-message="execPop2Message"
                        @check-mandatory="checkMandatory"
                        @exec-action="execAction"
                        @check-is-in-edit-mode-section="checkIsInEditModeSection"
                    />
                </td>
            </tr>
        </template>

        <template v-slot:expanded-row="{ item, internalItem }">
            <tr v-if="headersOnlyWithTextArea.length > 0">
                <td :colspan="headersWithOutTextArea.length">
                    <div v-for="(header, i) in headersOnlyWithTextArea" :key="i" class="pa-4">
                        <div v-if="checkVisibilitForComponent(header, item.index)">
                            <p class="text-body-2 font-weight-medium">{{ header.title }}</p>
                        </div>
                        <component
                            :is="header.type"
                            :id="trimStringToBeValidId(header.name) + '_' + header.id"
                            v-bind="{
                                ...header.props,
                                disabled: isDisabled(header, item.index) || GetDisabledRegister(disableRegister, disableRegisterItemId, item.index)
                            }"
                            :is-in-edit-mode="isInEditMode"
                            :record-index="item.index"
                            :value="header.type !== 'pop2-datepickerinput' ? item[header.key] : null"
                            :record-id="getRecordId(internalItem)"
                            :record-state="getRecordState(internalItem)"
                            no-label
                            is-in-table
                            :any-mandatory-component-is-empty="anyMandatoryComponentIsEmpty"
                            :screenUUID="screenUUID"
                            :component-name="header.name"
                            :component-type="header.type"
                            :component-id="header.id"
                            :section-name="sectionName"
                            @exec-method="execMethod"
                            @exec-code="execCode"
                            @exec-hyperlink="execHyperlink"
                            @exec-pop2-message="execPop2Message"
                            @check-mandatory="checkMandatory"
                            @exec-action="execAction"
                            @check-is-in-edit-mode-section="checkIsInEditModeSection"
                        />
                    </div>
                </td>
            </tr>
        </template>
    </v-data-table>
</template>

<script lang="ts">
// @ts-expect-error - Missing types
import { defineAsyncComponent } from "vue"

import Pop2Alert from "@/components/screenComponents/pop2-alert.vue"
import Pop2Avatar from "@/components/screenComponents/pop2-avatar.vue"
import Pop2Button from "@/components/screenComponents/pop2-button.vue"
import Pop2Calendar from "@/components/screenComponents/pop2-calendar.vue"
import Pop2Calendarpicker from "@/components/screenComponents/pop2-calendarpicker.vue"
import Pop2Checkbox from "@/components/screenComponents/pop2-checkbox.vue"
import Pop2Chip from "@/components/screenComponents/pop2-chip.vue"
import Pop2Currency from "@/components/screenComponents/pop2-currency.vue"
import Pop2Datepicker from "@/components/screenComponents/pop2-datepicker.vue"
import Pop2Datepickerinput from "@/components/screenComponents/pop2-datepickerinput.vue"
import Pop2Divider from "@/components/screenComponents/pop2-divider.vue"
import Pop2Hyperlink from "@/components/screenComponents/pop2-hyperlink.vue"
import Pop2Icon from "@/components/screenComponents/pop2-icon.vue"
import Pop2Image from "@/components/screenComponents/pop2-image.vue"
import Pop2Include from "@/components/screenComponents/pop2-include.vue"
import Pop2Input from "@/components/screenComponents/pop2-input.vue"
import Pop2Kebabmenu from "@/components/screenComponents/pop2-kebabmenu.vue"
import Pop2Label from "@/components/screenComponents/pop2-label.vue"
import Pop2Payrollconcepts from "@/components/screenComponents/pop2-payrollconcepts.vue"
import Pop2Rating from "@/components/screenComponents/pop2-rating.vue"
import Pop2Rectreeview from "@/components/screenComponents/pop2-rectreeview.vue"
import Pop2Search from "@/components/screenComponents/pop2-search.vue"
import Pop2Select from "@/components/screenComponents/pop2-select.vue"
import Pop2Slider from "@/components/screenComponents/pop2-slider.vue"
import Pop2Spacer from "@/components/screenComponents/pop2-spacer.vue"
import Pop2Stepper from "@/components/screenComponents/pop2-stepper.vue"
import Pop2Timepickerinput from "@/components/screenComponents/pop2-timepickerinput.vue"
import Pop2Timer from "@/components/screenComponents/pop2-timer.vue"
import Pop2Uploadfile from "@/components/screenComponents/pop2-uploadfile.vue"
import Pop2Urlbox from "@/components/screenComponents/pop2-urlbox.vue"
import Pop2Variant from "@/components/screenComponents/pop2-variant.vue"
import DataBinding from "@/data-provider/dataBinding"
import DataEntities from "@/data-provider/dataEntities"
import BindingMixin from "@/mixin/bindingMixin"
import DataListMixin from "@/mixin/dataListMixin"
import DataMixin from "@/mixin/dataMixin"
import GeneralMixin from "@/mixin/generalMixin"
import ScreenComponentMixin from "@/mixin/screenComponentMixin"
import { TExecutionContext, THeader } from "@/shared-types/TCommonInterfaces"
import { TNullableString, TNumberSizeInOneRow, TRecordState, TTablePagination } from "@/shared-types/TCommonTypes"
import { TEntityMetadata } from "@/shared-types/dataService/TDataServiceEntity"
import Formatter from "@/shared/formatter"
import General from "@/shared/general"
import HelperConverts from "@/shared/helperConverts"
import { useStUserActions } from "@/stores/stUserActions"
import cloneDeep from "lodash.clonedeep"
import { Component, Prop, mixins } from "vue-facing-decorator"

@Component({
    emits: ["exec-code", "check-mandatory", "changeRecordIndex", "addRegister", "removeRegister", "reset-validations", "change-table-options"],
    name: "Pop2Table",
    components: {
        Pop2Avatar,
        Pop2Button,
        Pop2Calendar,
        Pop2Calendarpicker,
        Pop2Chat: defineAsyncComponent(() => import("@/components/screenComponents/pop2-chat.vue")),
        Pop2Checkbox,
        Pop2Chip,
        Pop2Currency,
        Pop2Datepicker,
        Pop2Datepickerinput,
        Pop2Divider,
        Pop2Dmsmanager: defineAsyncComponent(() => import("@/components/screenComponents/pop2-dmsmanager.vue")),
        Pop2Dynamicfilter: defineAsyncComponent(() => import("@/components/screenComponents/pop2-dynamicfilter.vue")),
        Pop2Mailmerge: defineAsyncComponent(() => import("@/components/screenComponents/pop2-mailmerge.vue")),
        Pop2Gallery: defineAsyncComponent(() => import("@/components/screenComponents/pop2-gallery.vue")),
        Pop2Graph: defineAsyncComponent(() => import("@/components/screenComponents/pop2-graph.vue")),
        Pop2Group: defineAsyncComponent(() => import("@/components/screenComponents/pop2-group.vue")),
        Pop2Hyperlink,
        Pop2Icon,
        Pop2Image,
        Pop2Include,
        Pop2Input,
        Pop2Kebabmenu,
        Pop2Label,
        Pop2Pdfviewer: defineAsyncComponent(() => import("@/components/screenComponents/pop2-pdfviewer.vue")),
        Pop2Radiobuttongroup: defineAsyncComponent(() => import("@/components/screenComponents/pop2-radiobuttongroup.vue")),
        Pop2Rating,
        Pop2Search,
        Pop2Section: defineAsyncComponent(() => import("@/components/screenComponents/pop2-section.vue")),
        Pop2Select,
        Pop2Slider,
        Pop2Spacer,
        Pop2Stepper,
        Pop2Textarea: defineAsyncComponent(() => import("@/components/screenComponents/pop2-textarea.vue")),
        Pop2Timepickerinput,
        Pop2Timer,
        Pop2Uploadfile,
        Pop2Urlbox,
        Pop2Rectreeview,
        Pop2Alert,
        Pop2Payrollconcepts,
        Pop2Variant,
        Pop2Xmlviewer: defineAsyncComponent(() => import("@/components/screenComponents/pop2-xmlviewer.vue"))
    }
})
export default class Pop2Table extends mixins(BindingMixin) {
    @Prop({ type: Boolean }) alwaysVisible!: boolean
    @Prop({ type: Boolean }) allowAddRegister!: boolean
    @Prop({ type: Boolean }) allowRemoveRegister!: boolean
    @Prop({ type: String }) allowRemoveRegisterItemId!: string
    @Prop({ type: Boolean }) allowHeader!: boolean
    @Prop({ type: Boolean }) allowFooter!: boolean
    @Prop({ type: String }) alignHeader!: string

    @Prop({ type: Boolean }) tableDense!: boolean
    @Prop({ type: Boolean }) tableLayoutFixed!: boolean
    @Prop({ type: Boolean }) tableAllBorders!: boolean
    @Prop({ type: Number }) tableRowsPerPage!: number

    @Prop({ type: Array }) headers!: THeader[]
    @Prop({ type: Array }) values!: object[]
    @Prop({ type: Boolean }) oneRowTable!: boolean
    @Prop({ type: Number }) columnsInOneRow!: TNumberSizeInOneRow

    @Prop({ type: Boolean }) anyMandatoryComponentIsEmpty!: boolean
    @Prop({ type: Boolean }) allowSelect!: boolean
    @Prop({ type: String }) selectedItemId!: string
    @Prop({ type: String }) changeSelected!: string
    @Prop({ type: Boolean }) disableRegister!: boolean
    @Prop({ type: String }) disableRegisterItemId!: string

    @Prop({ type: String }) loadSectionMethodId!: string
    @Prop({ type: String }) totalNumberOfElementsMethodId!: string

    @Prop({ type: Boolean }) nLevelBodyTable!: boolean

    selected: object[] = []
    expanded: [] = []

    page: number = 1
    itemsPerPage: number = 5

    tablePagination: TTablePagination = {
        itemsPerPage: 5,
        page: 1
    }

    protected stUserActions: ReturnType<typeof useStUserActions> = useStUserActions()

    private vueInstance(): any {
        return this as any
    }

    private screenComponentMixin(): ScreenComponentMixin {
        return this as unknown as ScreenComponentMixin
    }

    private generalMixin(): GeneralMixin {
        return this as unknown as GeneralMixin
    }

    private bindingMixin(): BindingMixin {
        return this as unknown as BindingMixin
    }

    private dataListMixin(): DataListMixin {
        return this as unknown as DataListMixin
    }

    private dataMixin(): DataMixin {
        return this as unknown as DataMixin
    }

    // Vue Events
    created(): void {
        this.dataMixin().getCurrentScreen()
        this.itemsPerPage = this.tableRowsPerPage
        this.tablePagination.itemsPerPage = this.tableRowsPerPage
    }
    //vue methods
    mounted(): void {
        //To prevent the pagination from being read by screen readers (landmarks)
        this.vueInstance().$nextTick(() => {
            const el: any = this.vueInstance().$el.querySelector(".v-data-table-footer__pagination .v-pagination")
            if (el) {
                el.setAttribute("aria-hidden", "true")
            }
        })
    }

    // Computed
    get itemsPerPageOptions(): { value: number; title: string }[] {
        return this.loadSectionMethodId
            ? [
                  { value: 5, title: "5" },
                  { value: 10, title: "10" },
                  { value: 15, title: "15" },
                  { value: 20, title: "20" }
              ]
            : [
                  { value: 5, title: "5" },
                  { value: 10, title: "10" },
                  { value: 15, title: "15" },
                  { value: 20, title: "20" },
                  { value: -1, title: this.vueInstance().$t("todolist.all") }
              ]
    }

    get getAllowSelect(): boolean {
        if (this.allowSelect && this.selectedItemId) {
            return true
        }

        return false
    }

    get hideHeader(): boolean {
        if (this.values.length === 0) {
            return true
        }

        if (this.oneRowTable) {
            return true
        }

        if (!this.allowHeader) {
            return true
        }

        return false
    }

    get hideFooter(): boolean {
        if (this.values.length === 0) {
            return true
        }

        if (!this.loadSectionMethodId && this.values.length <= 5 && !this.screenComponentMixin().isInEditMode) {
            return true
        }

        if (this.oneRowTable || !this.allowFooter) {
            return true
        }

        return false
    }

    get headersWithOutTextArea(): THeader[] {
        const clonedHeader: THeader[] = cloneDeep(this.headers)
        let newHeader: THeader[] = []
        for (const element of clonedHeader) {
            if (General.getShow(element, this.generalMixin().isSmAndDown, this.generalMixin().isMd, this.generalMixin().isLgAndUp) && element.type !== "pop2-textarea") {
                if (this.screenComponentMixin().isInEditMode && element.props !== undefined && element.props.mandatory === true) {
                    if (element.title) {
                        element.mandatory = true
                    }
                }

                element.align = this.alignHeader

                newHeader.push(element)
            }
        }
        if (this.existAtLeastOneTextAreaComponent && this.headers?.at(-1)?.key !== "data-table-expand") {
            newHeader.push({ title: "", key: "data-table-expand" })
        }

        return newHeader
    }

    get headersWithoutHiddenHeaders(): THeader[] {
        // Important. This function is only valid for tables with one register (one row Table) or in mobile mode.
        const clonedHeader: THeader[] = cloneDeep(this.headers)
        let newHeader: THeader[] = []
        for (const element of clonedHeader) {
            if (General.getShow(element, this.generalMixin().isSmAndDown, this.generalMixin().isMd, this.generalMixin().isLgAndUp)) {
                const isVisible: boolean = this.oneRowTable && element?.props?.visible ? this.checkVisibilitForComponent(element, 0) : true
                if (isVisible) newHeader.push(element)
            }
        }
        return newHeader
    }

    get headersOnlyWithTextArea(): THeader[] {
        const clonedHeader: THeader[] = cloneDeep(this.headers)
        let newHeader: THeader[] = []
        for (const element of clonedHeader) {
            if (element.type === "pop2-textarea") {
                newHeader.push(element)
            }
        }

        return newHeader
    }

    get existAtLeastOneTextAreaComponent(): boolean {
        return this.headers.some((el: THeader) => el.type === "pop2-textarea")
    }

    // Methods
    getValueOneRow(header: THeader): any {
        if (this.values.length > 0) {
            const values: { [key: string]: string | number }[] = this.values[0] as { [key: string]: string | number }[]
            return header.type === "pop2-datepickerinput" ? null : values[header.key]
        }

        return null
    }

    getNumColumns(header: THeader): number {
        if (this.columnsInOneRow === 1) {
            return 12
        }

        return (12 / this.columnsInOneRow) * header.props.sizeInOneRow
    }

    getCellClass(header: THeader, index: number): string {
        if (header.props?.cellClass) {
            return this.screenComponentMixin().getPropertyValueOrName(header.props.cellClass, header.props.entityId, header.props.path, header.props.itemId, index)
        }

        return ""
    }

    getFooterString(): string {
        let totalNumberOfRecords: number | null = null

        if (this.loadSectionMethodId) {
            if (this.totalNumberOfElementsMethodId) {
                totalNumberOfRecords = this.dataMixin().getValue(null, this.dataMixin().entityId, this.dataMixin().path, this.totalNumberOfElementsMethodId, -1)
                totalNumberOfRecords = totalNumberOfRecords !== null && !Number.isNaN(Number(totalNumberOfRecords)) ? totalNumberOfRecords : null
            }
        } else {
            totalNumberOfRecords = this.values.length
        }

        const itemPerPage: number = this.itemsPerPage > -1 ? this.itemsPerPage : (totalNumberOfRecords ?? 0)
        let returnString: string = (itemPerPage * this.page - itemPerPage + 1).toString() + "-" + (itemPerPage * this.page).toString()
        if (totalNumberOfRecords) {
            returnString += " " + this.vueInstance().$t("of") + " " + totalNumberOfRecords
        }

        return returnString
    }

    isSelectedItem(item: any): any {
        let value: boolean | string | number = this.dataMixin().getValue(null, this.dataMixin().entityId, this.dataMixin().path, this.selectedItemId, item.index)
        value = HelperConverts.convertToBoolean(value)

        const index: number = this.selected.findIndex((x: any) => x?.index === item.index)
        if (index > -1 && !value) {
            this.selected.splice(index, 1)
        } else if (index === -1 && value) {
            this.selected.push(item)
        }

        return value
    }

    async selectAllItems(): Promise<void> {
        const initialRecord: number = this.tablePagination.itemsPerPage * this.tablePagination.page - this.tablePagination.itemsPerPage
        const endRecord: number = initialRecord + this.tablePagination.itemsPerPage

        for (let index: number = initialRecord; index < endRecord; index++) {
            await this.selectItem(!this.isSelectedItem({ index }), { index }, false)
        }

        this.executeChangeSelected(undefined)

        this.selected = []
    }

    async selectItem(isSelected: boolean, item: any, fireEvent: boolean = true): Promise<void> {
        if (this.getAllowSelect && !this.GetDisabledRegister(this.disableRegister, this.disableRegisterItemId, item.index)) {
            if (isSelected) {
                await this.dataListMixin().changeValue(this.dataMixin().entityId, this.dataMixin().path, this.selectedItemId, item.index, 1)
            } else {
                await this.dataListMixin().changeValue(this.dataMixin().entityId, this.dataMixin().path, this.selectedItemId, item.index, 0)
            }
            if (fireEvent) {
                this.executeChangeSelected(item.index)
            }
        }
    }

    executeChangeSelected(recordIndex: any): void {
        const executionContext: TExecutionContext = { entityId: this.dataMixin().entityId, path: this.dataMixin().path, itemId: this.selectedItemId, recordIndex }
        this.vueInstance().$emit("exec-code", this.changeSelected, executionContext)
    }

    getRecordState(item: any): TRecordState {
        if (item) {
            return item.recordState
        }

        return "Unchanged"
    }

    getRecordId(item: any): number | undefined {
        if (item) {
            return item.recordId
        }

        return undefined
    }

    checkDisabled(disabled: any, entityId: string, path: string, itemId: string, recordIndex: number): boolean {
        if (this.dataMixin().isItemVisibleByLocalization(entityId, path, itemId) === false) {
            return false
        }

        if (DataBinding.isCodeBinding(disabled)) {
            return this.bindingMixin().getResultFromExecuteCode(disabled, recordIndex)
        } else {
            return this.screenComponentMixin().getVisibleComponent(disabled, entityId, path, itemId, recordIndex)
        }
    }

    isDisabled(header: THeader, recordIndex: number): boolean {
        if (!this.screenComponentMixin().disabled && !header.props?.disabled) {
            return false
        }

        if (this.screenComponentMixin().disabled) {
            return this.checkDisabled(this.screenComponentMixin().disabled, this.dataMixin().entityId, this.dataMixin().path, this.dataMixin().itemId, this.dataMixin().recordIndex)
        } else {
            return this.checkDisabled(header.props.disabled, header.props.entityId, header.props.path, header.props.itemId, recordIndex)
        }
    }

    checkVisibilitForComponent(element: THeader, recordIndex: number): boolean {
        if (this.dataMixin().isItemVisibleByLocalization(element.props.entityId, element.props.path, element.props.itemId) === false) {
            return false
        }

        if (DataBinding.isCodeBinding(element.props.visible)) {
            return this.bindingMixin().getResultFromExecuteCode(element.props.visible)
        } else {
            return this.screenComponentMixin().getVisibleComponent(element.props.visible, element.props.entityId, element.props.path, element.props.itemId, recordIndex)
        }
    }

    checkVisibilityForRecord(headers: THeader[], recordIndex: number): boolean {
        for (const element of headers) {
            if (this.checkVisibilitForComponent(element, recordIndex)) return true
        }

        return false
    }

    showHeaderText(header: any): string {
        let doNotShowLabel: string | undefined

        if (header.type === "pop2-label" && header.props.itemDataToShow === "both") {
            doNotShowLabel = undefined
        } else {
            const doNotShowLabelsForTheseComponents: string[] = ["pop2-label", "pop2-hyperlink", "pop2-button", "pop2-image", "pop2-avatar", "pop2-icon"]
            doNotShowLabel = doNotShowLabelsForTheseComponents.find((component: string) => component === header.type)
        }

        return doNotShowLabel ? "" : header.title
    }

    clickRow(item: any, isSelected: boolean): void {
        this.selectItem(isSelected, item)
        this.vueInstance().$emit("changeRecordIndex", item.index + 1)
    }

    clickAddRegister(): void {
        this.stUserActions.addUserEvent(this.vueInstance().$props, this.vueInstance().$route, "click", "Add register")

        this.vueInstance().$emit("addRegister")

        setTimeout(() => {
            if (this.itemsPerPage === -1) {
                //All records, only one page
                this.page = 1
            } else {
                this.page = Math.ceil(this.values.length / this.itemsPerPage)
            }
        }, 100)
    }

    clickRemoveRegister(recordIndex: number): void {
        // this.stUserActions.addUserEvent(this.vueInstance().$props, this.vueInstance().$route, "click", "Remove register table")

        this.vueInstance().$emit("removeRegister", recordIndex)
    }

    checkMandatory(): void {
        this.vueInstance().$emit("check-mandatory")
    }

    // paginnation
    /*
     * page: Number of page displayed
     * itemsPerPage: items per page displayed (5, 10, 15,...)
     */
    updatePagination(options: TTablePagination): void {
        if (this.loadSectionMethodId) {
            this.generalMixin().stGeneral.showWaitDialog({ text: this.vueInstance().$t("app.defaultLoading") })
        }

        setTimeout(() => {
            this.doUpdatePagination(options)
        }, 1)
    }

    private async doUpdatePagination(options: TTablePagination): Promise<void> {
        if (this.loadSectionMethodId && !this.dataMixin().getIsListEnabled()) {
            const lastSeenrecord: number = this.page * this.itemsPerPage
            if (lastSeenrecord >= this.values.length) {
                const entityMetadata: TEntityMetadata | undefined = this.dataMixin().screen.entities.find((entityMetadata: TEntityMetadata) => entityMetadata.id === this.dataMixin().entityId)

                if (entityMetadata) {
                    await DataEntities.executeMethod(this.dataMixin().screenUUID, entityMetadata, this.dataMixin().path, this.loadSectionMethodId, [])
                }
            }
        }

        if (this.loadSectionMethodId) {
            this.$nextTick(() => {
                this.generalMixin().stGeneral.setShowWaitDialog(false)
            })
        }

        this.vueInstance().$emit("reset-validations")

        if (this.tablePagination.itemsPerPage !== options.itemsPerPage || this.tablePagination.page !== options.page) {
            this.tablePagination.itemsPerPage = options.itemsPerPage
            this.tablePagination.page = options.page

            this.vueInstance().$emit("change-table-options", options)
        }
    }

    setFunctionMouseOver2(recordIndex: number): void {
        // , event: any) {
        if (!this.dataMixin().isInDesignMode) {
            this.generalMixin().stScreen.setMouseOverRecordIndex(recordIndex)
            if (this.headers.length > 0 && this.headers[0].props) {
                this.generalMixin().stScreen.setMouseOverSectionId(this.headers[0].props.sectionId)
            }
        }
    }

    setFunctionMouseLeave2(): void {
        //event: any) {
        if (!this.dataMixin().isInDesignMode) {
            this.generalMixin().stScreen.setMouseOverRecordIndex(null)
            this.generalMixin().stScreen.setMouseOverSectionId(null)
        }
    }

    /**
     * It returns a valid id from a string
     * @param name - String to be formatted to match a valid id
     * @returns formatted string (alphanumeric and numeric chars + underscore )
     */
    trimStringToBeValidId(name: TNullableString | undefined): string {
        return Formatter.trimStringToBeValidId(name)
    }
}
</script>

<style lang="scss">
.pop2-table {
    & .v-select .v-field .v-field__input > input {
        display: none;
    }

    &.table-isSelectable tbody .tr-table:hover {
        cursor: pointer;
    }

    &:not(.table-all-borders) tbody .tr-table:nth-child(odd) {
        background-color: #f7f9fe;
    }

    &.table-mobile:not(.table-all-borders) tbody .tr-table:nth-child(odd) {
        background-color: unset;
    }

    &.table-all-borders table {
        & tr td {
            padding: 0 4px !important;
            border-right: thin solid rgba(var(--v-border-color), var(--v-border-opacity));

            &:first-child {
                border-left: thin solid rgba(var(--v-border-color), var(--v-border-opacity));
            }
        }
    }

    &.table-isInEditMode:not(.no-data) tbody tr td {
        vertical-align: top;
    }

    &.table-layout-fixed {
        table:not(table table) {
            table-layout: fixed;
            width: 100% !important;
        }
    }

    & .expandIcon.expanded {
        transform: rotate(180deg);
    }

    &.oneRowTable {
        & tr:hover {
            background-color: inherit !important;
        }

        & td {
            min-height: 48px;
            height: auto !important;

            &.view-desktop {
                &.tdExpandable {
                    border-bottom: none;
                }
                & .header {
                    min-width: 35%;
                    max-width: 35%;
                }
            }
        }
    }

    &.table-mobile {
        &.table-isInEditMode {
            & .v-input {
                width: 100%;
            }
        }
    }

    /* Fix Vuetify styles */
    & .v-data-table-footer__items-per-page > .v-select {
        width: auto !important;
        min-width: auto;
    }
}

.isWidget .oneRowTable td.view-desktop .header {
    min-width: 50%;
    max-width: 50%;
}

.width-50 {
    width: 50%;
}

.card-container {
    margin-bottom: 10px;
    padding: 10px 0px 10px 0px;
    border-color: #cbd3db;
    border-radius: 8px;
}

.pop2-table.table-mobile:not(.no-data) table {
    display: flex;
    flex-direction: column;
}
</style>

<!-- <style>
.pop2-table tbody .select-check-box .v-input--selection-controls {
    margin: 0;
    padding: 0;
}

.pop2-table.table-isInEditMode tbody .select-check-box .v-input--selection-controls {
    padding-top: 6px;
}

.pop2-table table thead th,
.pop2-table table tbody td,
.pop2-table .v-data-footer {
    border-color: #e6eaee !important;
}

.oneRowTable td.view-mobile,
.table-mobile .tr-table.border-bottom {
    border-bottom: thin solid rgba(0, 0, 0, 0.12);
}

/* Fix Vuetify */
.v-data-table > .v-data-table__wrapper > table {
    width: 99% !important;
}

.v-data-table.v-data-table--dense > .v-data-table__wrapper > table > tbody > tr > td {
    padding: 0 4px !important;
}

.v-data-table.v-data-table--dense > .v-data-table__wrapper {
    overflow: hidden;
}

.v-data-table.pop2-table.table-mobile thead.v-data-table-header.v-data-table-header-mobile tr {
    display: flex;
}

.v-data-table.pop2-table.table-mobile thead.v-data-table-header.v-data-table-header-mobile tr th {
    padding-left: 4px;
    padding-right: 4px;
    width: 100%;
}

.v-data-table.pop2-table.table-mobile thead.v-data-table-header.v-data-table-header-mobile tr th .v-data-table-header-mobile__select .v-input--selection-controls__input .v-icon.v-icon {
    top: 12px;
}

.v-data-table.pop2-table.table-mobile
    thead.v-data-table-header.v-data-table-header-mobile
    tr
    th
    .v-data-table-header-mobile__select
    .v-input--selection-controls__input
    .v-input--selection-controls__ripple {
    top: 0;
}

.v-data-table.pop2-table .v-text-field__details {
    margin-bottom: 0;
}

/* 
This fix the problem: The sort icon is moved below the header text if it doesn't fit
https://github.com/vuetifyjs/vuetify/issues/10164 
*/
.v-data-table-header th {
    white-space: nowrap;
}
</style> -->
