<!-- Simple Visual Rule Builder Component -->
<template>
	<div class="rule-builder">
		<div class="builder-section">
			<h4>Conditions</h4>
			<div class="condition-list">
				<div v-for="(condition, index) in conditions" :key="index" class="condition-row">
					<div class="form-group">
						<label>Field</label>
						<input type="text" v-model="condition.left.value" class="form-control" placeholder="fieldname">
					</div>
					<div class="form-group">
						<label>Operator</label>
						<select v-model="condition.operator" class="form-control">
							<option value="==">Equals</option>
							<option value="!=">Not Equals</option>
							<option value=">">Greater Than</option>
							<option value="<">Less Than</option>
							<option value=">=">Greater or Equal</option>
							<option value="<=">Less or Equal</option>
							<option value="contains">Contains</option>
							<option value="is_set">Is Set</option>
							<option value="is_not_set">Is Not Set</option>
						</select>
					</div>
					<div class="form-group" v-if="!['is_set', 'is_not_set'].includes(condition.operator)">
						<label>Value</label>
						<input type="text" v-model="condition.right.value" class="form-control" placeholder="value">
					</div>
					<div class="form-group">
						<label>Logic</label>
						<select v-model="condition.logical_operator" class="form-control">
							<option value="AND">AND</option>
							<option value="OR">OR</option>
						</select>
					</div>
					<button @click="removeCondition(index)" class="btn btn-danger btn-sm">
						<i class="fa fa-times"></i>
					</button>
				</div>
			</div>
			<button @click="addCondition" class="btn btn-primary btn-sm">
				<i class="fa fa-plus"></i> Add Condition
			</button>
		</div>

		<div class="builder-section">
			<h4>Actions</h4>
			<div class="action-list">
				<div v-for="(action, index) in actions" :key="index" class="action-row">
					<div class="form-group">
						<label>Action Type</label>
						<select v-model="action.type" class="form-control">
							<option value="set_field">Set Field Value</option>
							<option value="raise_error">Raise Error</option>
							<option value="raise_warning">Raise Warning</option>
							<option value="log_issue">Log Issue</option>
							<option value="call_method">Call Method</option>
						</select>
					</div>
					<div class="form-group" v-if="action.type === 'set_field'">
						<label>Field Name</label>
						<input type="text" v-model="action.field" class="form-control" placeholder="fieldname">
					</div>
					<div class="form-group" v-if="action.type === 'set_field'">
						<label>Value</label>
						<input type="text" v-model="action.value.value" class="form-control" placeholder="value">
					</div>
					<div class="form-group" v-if="['raise_error', 'raise_warning', 'log_issue'].includes(action.type)">
						<label>Message</label>
						<input type="text" v-model="action.message" class="form-control" placeholder="message">
					</div>
					<div class="form-group" v-if="action.type === 'log_issue'">
						<label>Severity</label>
						<select v-model="action.severity" class="form-control">
							<option value="High">High</option>
							<option value="Medium">Medium</option>
							<option value="Low">Low</option>
						</select>
					</div>
					<button @click="removeAction(index)" class="btn btn-danger btn-sm">
						<i class="fa fa-times"></i>
					</button>
				</div>
			</div>
			<button @click="addAction" class="btn btn-primary btn-sm">
				<i class="fa fa-plus"></i> Add Action
			</button>
		</div>

		<div class="builder-actions">
			<button @click="saveToForm" class="btn btn-success">
				<i class="fa fa-save"></i> Save to Form
			</button>
			<button @click="loadFromForm" class="btn btn-default">
				<i class="fa fa-refresh"></i> Load from Form
			</button>
		</div>
	</div>
</template>

<script>
export default {
	name: 'RuleBuilder',
	data() {
		return {
			conditions: [],
			actions: []
		};
	},
	mounted() {
		this.loadFromForm();
	},
	methods: {
		addCondition() {
			this.conditions.push({
				left: {type: 'field', value: ''},
				operator: '==',
				right: {type: 'literal', value: ''},
				logical_operator: 'AND'
			});
		},
		removeCondition(index) {
			this.conditions.splice(index, 1);
		},
		addAction() {
			this.actions.push({
				type: 'set_field',
				field: '',
				value: {type: 'literal', value: ''}
			});
		},
		removeAction(index) {
			this.actions.splice(index, 1);
		},
		loadFromForm() {
			// Load from Frappe form
			const frm = cur_frm;
			if (frm) {
				try {
					if (frm.doc.conditions_json) {
						this.conditions = JSON.parse(frm.doc.conditions_json);
					}
					if (frm.doc.actions_json) {
						this.actions = JSON.parse(frm.doc.actions_json);
					}
				} catch (e) {
					frappe.msgprint('Error loading from form: ' + e.message);
				}
			}
		},
		saveToForm() {
			// Save to Frappe form
			const frm = cur_frm;
			if (frm) {
				frm.set_value('conditions_json', JSON.stringify(this.conditions, null, 2));
				frm.set_value('actions_json', JSON.stringify(this.actions, null, 2));
				frappe.show_alert({
					message: 'Saved to form',
					indicator: 'green'
				});
			}
		}
	}
};
</script>

<style scoped>
.rule-builder {
	padding: 15px;
	background: #f9f9f9;
	border-radius: 4px;
}

.builder-section {
	margin-bottom: 20px;
	padding: 15px;
	background: white;
	border-radius: 4px;
	border: 1px solid #ddd;
}

.builder-section h4 {
	margin-top: 0;
	margin-bottom: 15px;
	color: #333;
	font-weight: 600;
}

.condition-row,
.action-row {
	display: flex;
	gap: 10px;
	margin-bottom: 10px;
	padding: 10px;
	background: #f5f5f5;
	border-radius: 4px;
	align-items: flex-end;
}

.form-group {
	flex: 1;
	min-width: 150px;
}

.form-group label {
	display: block;
	font-size: 12px;
	font-weight: 500;
	margin-bottom: 5px;
	color: #666;
}

.form-group input,
.form-group select {
	width: 100%;
	padding: 6px 10px;
	font-size: 13px;
	border: 1px solid #d1d8dd;
	border-radius: 3px;
}

.builder-actions {
	margin-top: 20px;
	display: flex;
	gap: 10px;
}

button {
	display: inline-flex;
	align-items: center;
	gap: 5px;
}
</style>
