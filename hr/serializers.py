# # # hr/serializers.py
# # from rest_framework import serializers
# # from .models import Payslip, LeaveRequest, CompanyPolicy, PerformanceReview, Goal, Payroll

# # class PayslipSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Payslip
# #         fields = '__all__'

# # class LeaveRequestSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = LeaveRequest
# #         fields = '__all__'

# # class CompanyPolicySerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = CompanyPolicy
# #         fields = '__all__'

# # class PerformanceReviewSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = PerformanceReview
# #         fields = '__all__'

# # class GoalSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Goal
# #         fields = '__all__'

# # class BenefitSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Benefit
# #         fields = '__all__'

# # class WorkerBenefitSerializer(serializers.ModelSerializer):
# #     benefit_name = serializers.CharField(source='benefit.name', read_only=True)
# #     class Meta:
# #         model = WorkerBenefit
# #         fields = ['id', 'worker', 'benefit', 'benefit_name', 'enrolled_at', 'contribution_amount', 
# #                   'deduction_period', 'is_active', 'end_date']

# # class PayrollSerializer(serializers.ModelSerializer):
# #     class Meta:
# #         model = Payroll
# #         fields = ['id', 'worker', 'period', 'base_salary', 'bonuses', 'breakdown', 'total', 'created_at']
# # hr/serializers.py
# # hr/serializers.py
# from rest_framework import serializers
# from .models import Payslip, LeaveRequest, CompanyPolicy, PerformanceReview, Goal

# class PayslipSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payslip
#         fields = '__all__'

# class LeaveRequestSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeaveRequest
#         fields = '__all__'

# class CompanyPolicySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CompanyPolicy
#         fields = '__all__'

# class PerformanceReviewSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PerformanceReview
#         fields = '__all__'

# class GoalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Goal
#         fields = '__all__'
# hr/serializers.py
from rest_framework import serializers
from .models import Payslip, LeaveRequest, CompanyPolicy, PerformanceReview, Goal

class PayslipSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)

    class Meta:
        model = Payslip
        fields = ['id', 'worker', 'worker_username', 'period', 'amount', 'created_at']

    def validate(self, data):
        if data['amount'] <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return data

class LeaveRequestSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'worker', 'worker_username', 'start_date', 'end_date', 'reason', 'status', 'created_at']

    def validate(self, data):
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

class CompanyPolicySerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = CompanyPolicy
        fields = ['id', 'title', 'content', 'organization', 'organization_name']

class PerformanceReviewSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)

    class Meta:
        model = PerformanceReview
        fields = ['id', 'worker', 'worker_username', 'reviewer', 'reviewer_username', 'score', 'comments', 'review_date']

    def validate(self, data):
        if data['score'] < 0 or data['score'] > 100:  # Assuming score is 0-100
            raise serializers.ValidationError("Score must be between 0 and 100.")
        return data

class GoalSerializer(serializers.ModelSerializer):
    worker_username = serializers.CharField(source='worker.user.username', read_only=True)

    class Meta:
        model = Goal
        fields = ['id', 'worker', 'worker_username', 'description', 'deadline', 'status']

    def validate(self, data):
        if data['deadline'] < data.get('created_at', timezone.now().date()):
            raise serializers.ValidationError("Deadline must be in the future.")
        return data