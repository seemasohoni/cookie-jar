package core;

import java.util.concurrent.atomic.AtomicInteger;

// Define sealed interfaces for Milestone Types
sealed interface Milestone permits CookieMilestone, StreakMilestone, GeneralMilestone {}

record CookieMilestone(int targetCookies, String rewardName) implements Milestone {}
record StreakMilestone(int requiredDays, String badgeName) implements Milestone {}
record GeneralMilestone(String description) implements Milestone {}

public class MilestoneService {

    // Thread-safe storage for the user's cookies
    private final AtomicInteger cookieCount;

    public MilestoneService(int initialCookies) {
        this.cookieCount = new AtomicInteger(initialCookies);
    }

    public int getCookieCount() {
        return cookieCount.get();
    }

    public void addCookies(int amount) {
        if (amount > 0) {
            cookieCount.addAndGet(amount);
        }
    }

    /**
     * Evaluates a milestone based on current progress using Pattern Matching for switch (Java 21+).
     * @param milestone The milestone to evaluate
     * @return A message describing the reward status
     */
    public String evaluateMilestone(Milestone milestone) {
        int currentCookies = cookieCount.get();

        return switch (milestone) {
            case CookieMilestone m when currentCookies >= m.targetCookies() -> 
                "Unlocked: " + m.rewardName() + " (Target reached: " + m.targetCookies() + " cookies)";
            case CookieMilestone m -> 
                "Keep going! You need " + (m.targetCookies() - currentCookies) + " more cookies for " + m.rewardName();
            
            case StreakMilestone m -> 
                "Streak Milestone tracking... (requires external streak value)";
            
            case GeneralMilestone m -> 
                "General Milestone: " + m.description();
        };
    }
}
