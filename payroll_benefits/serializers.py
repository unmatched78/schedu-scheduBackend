# # payroll_benefits/serializers.py
# from rest_framework import serializers
# from .models import Benefit, WorkerBenefit, PayrollSettings, Payroll

# class BenefitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Benefit
#         fields = '__all__'

# class WorkerBenefitSerializer(serializers.ModelSerializer):
#     benefit_name = serializers.CharField(source='benefit.name', read_only=True)
#     class Meta:
#         model = WorkerBenefit
#         fields = ['id', 'worker', 'benefit', 'benefit_name', 'enrolled_at', 'contribution_amount', 
#                   'deduction_period', 'is_active', 'end_date']

# class PayrollSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PayrollSettings
#         fields = ['id', 'worker', 'base_salary', 'default_bonuses', 'default_deductions', 'updated_at']

# class PayrollSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payroll
#         fields = ['id', 'worker', 'period', 'base_salary', 'bonuses', 'breakdown', 'total', 'created_at']
# payroll_benefits/serializers.py
from rest_framework import serializers
from .models import Benefit, WorkerBenefit, PayrollSettings, Payroll
from core.models import Worker

class BenefitSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Benefit
        fields = ['id', 'organization', 'organization_name', 'name', 'benefit_type', 'description', 
                  'default_cost', 'deduction_frequency', 'enrollment_start', 'enrollment_end', 
                  'is_active', 'created_at', 'updated_at']

    def validate(self, data):
        if data['default_cost'] < 0:
            raise serializers.ValidationError("Default cost cannot be negative.")
        if data.get('enrollment_start') and data.get('enrollment_end') and data['enrollment_start'] > data['enrollment_end']:
            raise serializers.ValidationError("Enrollment end date must be after start date.")
        return data

class WorkerBenefitSerializer(serializers.ModelSerializer):
    benefit_name = serializers.CharField(source='benefit.name', read_only=True)
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)

    class Meta:
        model = WorkerBenefit
        fields = ['id', 'worker', 'worker_username', 'benefit', 'benefit_name', 'enrolled_at', 
                  'contribution_amount', 'deduction_period', 'is_active', 'end_date']

    def validate(self, data):
        if data['contribution_amount'] < 0:
            raise serializers.ValidationError("Contribution amount cannot be negative.")
        if WorkerBenefit.objects.filter(
            worker=data['worker'], 
            benefit=data['benefit'], 
            deduction_period=data['deduction_period']
        ).exists():
            raise serializers.ValidationError("This worker is already enrolled in this benefit for this period.")
        return data

class PayrollSettingsSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)

    class Meta:
        model = PayrollSettings
        fields = ['id', 'worker', 'worker_username', 'base_salary', 'default_bonuses', 
                  'default_deductions', 'updated_at']

    def validate(self, data):
        if data['base_salary'] <= 0:
            raise serializers.ValidationError("Base salary must be positive.")
        if data['default_bonuses'] < 0:
            raise serializers.ValidationError("Default bonuses cannot be negative.")
        if any(float(value) < 0 for value in data['default_deductions'].values()):
            raise serializers.ValidationError("Default deductions cannot contain negative values.")
        return data

class PayrollSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)

    class Meta:
        model = Payroll
        fields = ['id', 'worker', 'worker_username', 'period', 'base_salary', 'bonuses', 
                  'breakdown', 'total', 'created_at']