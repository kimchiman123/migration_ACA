package com.aivle0102.bigproject.controller;

import com.aivle0102.bigproject.domain.ConsumerFeedback;
import com.aivle0102.bigproject.dto.EvaluationRequest;
import com.aivle0102.bigproject.service.EvaluationService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/evaluation")
public class EvaluationController {

    private final EvaluationService evaluationService;

    // Í∞?AI ?¨ÏÇ¨?ÑÏõê?êÍ≤å ?ùÏÑ±??Î≥¥Í≥†?úÎ? ?†Î?Î°??âÍ? ÏßÑÌñâ
    @PostMapping
    public List<ConsumerFeedback> evaluateByPersonas(@RequestBody EvaluationRequest request) {
        return evaluationService.evaluate(request.getPersonas(), request.getReport());
    }
}

